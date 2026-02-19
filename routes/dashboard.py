from flask import Blueprint, render_template, jsonify, session, current_app
from flask_login import login_required, current_user
from models import db, Equipment, WorkOrder, KPISnapshot, Failure, ServiceLog, ServiceStatus
from sqlalchemy import func, desc
from datetime import datetime, timedelta, date
import pandas as pd
import os
import logging
import sys
from utils.project_manager import ProjectManager
from utils.backup_manager import BackupManager

# Setup logger with UTF-8 encoding
logging.basicConfig(stream=sys.stdout, encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_tram_ids_from_veriler(project_code=None):
    """Veriler.xlsx'den equipment_code'leri yükle - Proje bazlı"""
    if project_code is None:
        project_code = session.get('current_project', 'belgrad')
    
    veriler_file = ProjectManager.get_veriler_file(project_code)
    
    if not veriler_file or not os.path.exists(veriler_file):
        # Fallback: Equipment tablosundan çek
        return [eq.equipment_code for eq in Equipment.query.filter_by(parent_id=None, project_code=project_code).all()]
    
    try:
        df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
        # equipment_code sütununu kullan (eğer varsa), yoksa tram_id'leri string'e çevir
        if 'equipment_code' in df.columns:
            equipment_codes = df['equipment_code'].dropna().unique().tolist()
            return [str(c) for c in equipment_codes]
        elif 'tram_id' in df.columns:
            tram_ids = df['tram_id'].dropna().unique().tolist()
            return [str(t) for t in tram_ids]
        # Fallback: Equipment tablosundan çek
        return [eq.equipment_code for eq in Equipment.query.filter_by(parent_id=None, project_code=project_code).all()]
    except Exception as e:
        logger.error(f'Veriler.xlsx okuma hatasi ({project_code}): {e}')
        # Fallback: Equipment tablosundan çek
        return [eq.equipment_code for eq in Equipment.query.filter_by(parent_id=None, project_code=project_code).all()]

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def get_failures_from_excel(project_code=None):
    """Excel dosyasından arıza verilerini oku - Proje bazlı"""
    if not project_code:
        project_code = session.get('current_project', 'belgrad')
    
    # ProjectManager'dan Fracas dosyasını al
    ariza_listesi_file = ProjectManager.get_fracas_file(project_code)
    
    if not ariza_listesi_file or not os.path.exists(ariza_listesi_file):
        return [], {}
    
    try:
        # Path'e göre header satırını belirle
        if 'logs' in ariza_listesi_file and 'ariza_listesi' in ariza_listesi_file:
            header_row = 3
        else:
            header_row = 0
        
        df = pd.read_excel(ariza_listesi_file, sheet_name='FRACAS', header=header_row)
        
        # Son 5 açık arızayı al (son 5 satır)
        recent = df.tail(5).to_dict('records') if len(df) > 0 else []
        
        # Arıza sınıfı istatistikleri
        sinif_counts = {}
        for col in df.columns:
            if 'arıza' in col.lower() and 'sınıf' in col.lower():
                sinif_counts = df[col].value_counts().to_dict()
                break
        
        return recent, sinif_counts
    except Exception as e:
        logger.error(f'Excel okuma hatasi ({project_code}): {e}')
        return [], {}


def get_today_completed_failures_count():
    """Excel Arıza Listesi'nden bugünün tamamlanan arızalarını say - Proje-dinamik"""
    from flask import current_app
    
    current_project = session.get('current_project', 'belgrad')
    ariza_dir = os.path.join(current_app.root_path, 'logs', current_project, 'ariza_listesi')
    
    # Arıza Listesi dosyasını bul
    ariza_listesi_file = None
    if os.path.exists(ariza_dir):
        for file in os.listdir(ariza_dir):
            if file.endswith('.xlsx') and not file.startswith('~$'):
                ariza_listesi_file = os.path.join(ariza_dir, file)
                break
    
    if not ariza_listesi_file:
        return 0
    
    try:
        df = pd.read_excel(ariza_listesi_file, sheet_name='Ariza Listesi', header=3)
        
        # Bugünün tarihi
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        
        # Tarih ve durum sütunlarını bul
        tarih_col = None
        durum_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if tarih_col is None and ('tarih' in col_lower or 'date' in col_lower):
                tarih_col = col
            if durum_col is None and ('durum' in col_lower or 'status' in col_lower):
                durum_col = col
        
        if tarih_col is None or durum_col is None:
            return 0
        
        # Bugünün verileri ve "Kaydedildi" durumundaki arızaları filtrele
        today_completed = 0
        for idx, row in df.iterrows():
            try:
                # Tarih kontrolü
                tarih = row[tarih_col]
                if pd.isna(tarih):
                    continue
                
                # Tarih stringine çevir
                tarih_str = pd.Timestamp(tarih).strftime('%Y-%m-%d')
                
                # Bugünün mü?
                if tarih_str == today_str:
                    # Durum kontrolü
                    durum = str(row[durum_col]).strip() if not pd.isna(row[durum_col]) else ''
                    
                    # "Kaydedildi" statusu = tamamlanan
                    if durum == 'Kaydedildi':
                        today_completed += 1
            except Exception as e:
                logger.error(f'Satir islenirken hata ({idx}): {e}')
                continue
        
        return today_completed
    except Exception as e:
        logger.error(f"Excel'den bugunun tamamlanan ariza sayisi alinirken hata: {e}")
        return 0


def get_ariza_counts_by_class():
    """Excel'den arızaları sınıflara göre say (A, B, C, D) - Proje-dinamik"""
    from flask import current_app
    
    current_project = session.get('current_project', 'belgrad')
    ariza_dir = os.path.join(current_app.root_path, 'logs', current_project, 'ariza_listesi')
    
    # FRACAS dosyasını bul - Öncelik: ProjectManager'dan al
    ariza_listesi_file = ProjectManager.get_fracas_file(current_project)
    
    # Fallback: Eğer ProjectManager'dan bulunamazsa manuel ara
    if not ariza_listesi_file or not os.path.exists(ariza_listesi_file):
        if os.path.exists(ariza_dir):
            # Fracas dosyasını spesifik olarak ara
            for file in ['Fracas_BELGRAD.xlsx', 'Fracas_BELGRAD.xlsx', 'BEL25_FRACAS.xlsx']:
                test_file = os.path.join(ariza_dir, file)
                if os.path.exists(test_file):
                    ariza_listesi_file = test_file
                    break
            
            # Hala bulunamazsa, içinde 'FRACAS' veya 'Fracas' olan dosya ara
            if not ariza_listesi_file:
                for file in os.listdir(ariza_dir):
                    if file.endswith('.xlsx') and not file.startswith('~$') and ('FRACAS' in file.upper() or 'Fracas' in file):
                        ariza_listesi_file = os.path.join(ariza_dir, file)
                        break
            
            # Son çare: ilk xlsx dosyası
            if not ariza_listesi_file:
                for file in os.listdir(ariza_dir):
                    if file.endswith('.xlsx') and not file.startswith('~$'):
                        ariza_listesi_file = os.path.join(ariza_dir, file)
                        break
    
    # Sınıf tanımları
    class_definitions = {
        'A': 'A-Kritik/Emniyet Riski',
        'B': 'B-Yüksek/Operasyon Engeller',
        'C': 'C-Hafif/Kısıtlı Operasyon',
        'D': 'D-Arıza Değildir'
    }
    
    # Başlangıçta tüm sınıfları 0 ile init et
    counts = {
        'A': {'label': 'A-Kritik/Emniyet Riski', 'count': 0},
        'B': {'label': 'B-Yüksek/Operasyon Engeller', 'count': 0},
        'C': {'label': 'C-Hafif/Kısıtlı Operasyon', 'count': 0},
        'D': {'label': 'D-Arıza Değildir', 'count': 0}
    }
    
    if not ariza_listesi_file:
        logger.warning(f'FRACAS dosyası bulunamadı')
        return counts
    
    logger.debug(f'FRACAS dosyası: {os.path.basename(ariza_listesi_file)}')
    
    try:
        # Header row'u belirle - logs klasöründe ise 3, yoksa 0
        header_row = 3 if 'logs' in ariza_listesi_file and 'ariza_listesi' in ariza_listesi_file else 0
        df = pd.read_excel(ariza_listesi_file, sheet_name='FRACAS', header=header_row)
        
        # Arıza sınıfı sütununu bul
        sinif_col = None
        for col in df.columns:
            if 'arıza' in col.lower() and 'sınıf' in col.lower():
                sinif_col = col
                break
        
        if sinif_col:
            # Her arızayı kategorize et
            for sinif in df[sinif_col].dropna():
                sinif_str = str(sinif).strip()
                
                # Sınıfın ilk harfini al (A, B, C, D)
                if sinif_str.startswith('A'):
                    counts['A']['count'] += 1
                elif sinif_str.startswith('B'):
                    counts['B']['count'] += 1
                elif sinif_str.startswith('C'):
                    counts['C']['count'] += 1
                elif sinif_str.startswith('D'):
                    counts['D']['count'] += 1
            logger.debug(f'Ariza sınıfı sayıları: {counts}')
        else:
            logger.warning(f'Ariza sınıfı sütunu bulunamadı. Mevcut sütunlar: {list(df.columns)}')
        
        return counts
    except Exception as e:
        logger.error(f'Ariza sinifi hesaplama hatasi: {e}')
        import traceback
        logger.error(traceback.format_exc())
        return counts


def calculate_fleet_mttr():
    """
    Filo için MTTR (Mean Time To Repair - Ortalama Tamir Süresi) hesapla
    
    MTTR Formülü:
    MTTR = Toplam Tamir Süresi (dakika) / Toplam Arıza Sayısı
    
    Açıklama:
    - MTTR arızanın tamir edilmesine kadar geçen ortalama süreyi gösterir
    - Yüksek MTTR = daha uzun tamir süreleri (bakım verimsizliği)
    - Düşük MTTR = daha kısa tamir süreleri (bakım verimliliği)
    - Unit: Dakika (dk) veya Saat:Dakika formatında
    
    Örnek:
    - Toplam Tamir Süresi: 50,000 dakika
    - Toplam Arızalar: 100
    - MTTR = 50,000 / 100 = 500 dakika = 8 saat 20 dakika
      (Her arıza ortalama 8 saat 20 dakikada tamir edilir)
    
    Veri Kaynağı: Excel'deki "MTTR (dk)" sütunu ("61 dk", "120 dk" gibi format)
    """
    from flask import current_app
    import re
    
    try:
        current_project = session.get('current_project', 'belgrad')
        
        # Excel dosyasını bul
        ariza_dir = os.path.join(current_app.root_path, 'logs', current_project, 'ariza_listesi')
        ariza_listesi_file = None
        
        if os.path.exists(ariza_dir):
            for file in os.listdir(ariza_dir):
                if file.endswith('.xlsx') and not file.startswith('~$'):
                    ariza_listesi_file = os.path.join(ariza_dir, file)
                    break
        
        mttr_minutes = 0
        total_failures = 0
        
        if ariza_listesi_file:
            try:
                df = pd.read_excel(ariza_listesi_file, sheet_name='Ariza Listesi', header=3)
                
                # "MTTR (dk)" sütununu ara
                mttr_col = None
                for col in df.columns:
                    if 'mttr' in col.lower() and 'dk' in col.lower():
                        mttr_col = col
                        break
                
                # Eğer MTTR sütunu varsa, ortalamasını hesapla
                if mttr_col:
                    mttr_values = []
                    
                    # Excel verisi "120 dk", "61 dk" gibi string formatında olabilir
                    for val in df[mttr_col].dropna():
                        try:
                            val_str = str(val).strip()
                            # Metin içinden sayıyı çıkar (regex)
                            # "120 dk", "120", vb. formatları destekle
                            match = re.search(r'(\d+(?:[\.,]\d+)?)', val_str)
                            if match:
                                # Virgül veya nokta ayracını düzelt
                                number_str = match.group(1).replace(',', '.')
                                mttr_values.append(float(number_str))
                        except:
                            continue
                    
                    if len(mttr_values) > 0:
                        mttr_minutes = sum(mttr_values) / len(mttr_values)
                        mttr_minutes = round(mttr_minutes, 1)
                        total_failures = len(mttr_values)
                        logger.debug(f'[MTTR DEBUG] {len(mttr_values)} arizadan MTTR ortalamasi: {mttr_minutes} dk')
                    else:
                        # Fallback: Tüm arızaları say
                        total_failures = len(df[df.iloc[:, 0].notna()])
                        logger.debug(f'[MTTR DEBUG] MTTR degeri bulunamadi, fallback: {total_failures} ariza')
                else:
                    # MTTR sütunu yoksa tüm arızaları say
                    total_failures = len(df[df.iloc[:, 0].notna()])
                    logger.debug(f'[MTTR DEBUG] MTTR sutunu bulunamadi, fallback: {total_failures} ariza')
            
            except Exception as e:
                logger.error(f'[MTTR DEBUG] Excel MTTR okuma hatasi: {e}')
                import traceback
                logger.error(traceback.format_exc())
                total_failures = 0
                mttr_minutes = 0
        
        # Dakikayı saat:dakika formatına dönüştür
        hours = int(mttr_minutes // 60) if mttr_minutes > 0 else 0
        minutes = int(mttr_minutes % 60) if mttr_minutes > 0 else 0
        mttr_formatted = f"{int(mttr_minutes)} dk" if mttr_minutes > 0 else "0 dk"
        
        logger.debug(f'[MTTR FINAL] mttr_minutes={mttr_minutes}, formatted={mttr_formatted}, failures={total_failures}')
        
        return {
            'mttr_minutes': mttr_minutes,
            'mttr_formatted': mttr_formatted,  # "8h 20m" formatı
            'mttr_hours': round(mttr_minutes / 60, 1),  # Saat cinsinden
            'total_failures': total_failures,
            'unit': 'dakika (dk)'
        }
    
    except Exception as e:
        logger.error(f'[MTTR ERROR] MTTR hesaplama hatasi: {e}')
        import traceback
        logger.error(traceback.format_exc())
        return {
            'mttr_minutes': 0,
            'mttr_formatted': '0m',
            'mttr_hours': 0,
            'total_failures': 0,
            'unit': 'dakika (dk)'
        }


@bp.route('/')
@login_required
def index():
    """Ana dashboard - Genel bakış"""
    
    current_project = session.get('current_project', 'belgrad')
    
    # Ekipman durumu özeti
    equipment_stats = db.session.query(
        Equipment.status,
        func.count(Equipment.id)
    ).filter_by(parent_id=None, project_code=current_project).group_by(Equipment.status).all()
    
    equipment_summary = {status: count for status, count in equipment_stats}
    
    # İş emri durumu özeti
    wo_stats = db.session.query(
        WorkOrder.status,
        func.count(WorkOrder.id)
    ).group_by(WorkOrder.status).all()
    
    wo_summary = {status: count for status, count in wo_stats}
    
    # Kritik öncelikli açık iş emirleri
    critical_work_orders = WorkOrder.query.filter(
        WorkOrder.priority == 'critical',
        WorkOrder.status.in_(['pending', 'scheduled', 'in_progress'])
    ).order_by(WorkOrder.planned_start).limit(10).all()
    
    # Yaklaşan bakımlar (7 gün içinde)
    upcoming_maintenance = WorkOrder.query.filter(
        WorkOrder.status.in_(['pending', 'scheduled']),
        WorkOrder.planned_start >= datetime.utcnow(),
        WorkOrder.planned_start <= datetime.utcnow() + timedelta(days=7)
    ).order_by(WorkOrder.planned_start).limit(10).all()
    
    # Son arızalar - Excel'den çek
    recent_failures, ariza_sinif_counts = get_failures_from_excel()
    
    # Son KPI'lar
    latest_kpi = KPISnapshot.query.order_by(
        KPISnapshot.snapshot_date.desc()
    ).first()
    
    # ===== Tramvay Filozofu - Database'den 1531-1555 range'ini al =====
    # Belgrad projesinde 1531-1555 range'i kullan
    tramvaylar = Equipment.query.filter(
        Equipment.equipment_code >= '1531',
        Equipment.equipment_code <= '1555',
        Equipment.parent_id == None,
        Equipment.project_code == current_project
    ).order_by(Equipment.equipment_code).all()
    
    logger.debug(f'[DASHBOARD FILTER 1531-1555] Found {len(tramvaylar)} trams')
    
    # Eğer range'de veri yoksa fallback
    if not tramvaylar:
        logger.debug(f'[DASHBOARD FALLBACK] No trams in 1531-1555 range, using all project equipment')
        tramvaylar = Equipment.query.filter_by(parent_id=None, project_code=current_project).order_by(Equipment.equipment_code).all()
        logger.debug(f'[DASHBOARD FALLBACK] Found {len(tramvaylar)} trams from fallback')
    
    # Bugünün tarihi
    today = str(date.today())
    
    # Her tramvay için bugünün ServiceStatus kaydını al
    tramvay_statuses = []
    for tramvay in tramvaylar:
        # ServiceStatus'ten bugünün kaydını getir
        status_record = ServiceStatus.query.filter_by(
            tram_id=tramvay.equipment_code,
            date=today
        ).first()
        
        # Durum belirle
        status_display = 'aktif'
        status_color = 'success'
        status_from_db = 'Servis'
        
        if status_record:
            status_value = status_record.status if status_record.status else 'Servis'
            aciklama = status_record.aciklama if status_record.aciklama else ''
            
            # Status'u belirle - DB exact match
            if status_value == 'İşletme Kaynaklı Servis Dışı' or 'İşletme' in status_value:
                # İşletme Kaynaklı Servis Dışı = turuncu (işletme kaynaklı arıza)
                status_display = 'işletme'
                status_color = 'warning'
                status_from_db = 'İşletme Kaynaklı Servis Dışı'
            elif status_value == 'Servis Dışı' or 'Dışı' in status_value:
                # Servis Dışı = arızalı (kırmızı)
                status_display = 'ariza'
                status_color = 'danger'
                status_from_db = 'Servis Dışı'
            else:
                # Servis = aktif (yeşil)
                status_display = 'aktif'
                status_color = 'success'
                status_from_db = 'Servis'
        
        tramvay_statuses.append({
            'id': tramvay.id,
            'equipment_code': tramvay.equipment_code,
            'name': tramvay.name,
            'location': tramvay.location if hasattr(tramvay, 'location') else '',
            'total_km': tramvay.total_km if hasattr(tramvay, 'total_km') else 0,
            'current_km': tramvay.current_km if hasattr(tramvay, 'current_km') else 0,
            'status': status_display,
            'status_db': status_from_db,
            'status_color': status_color
        })
    
    # Toplam arızaları getir - SADECE Excel'den çek, Database'den değil
    son_arizalar_list, _ = get_failures_from_excel()
    son_arizalar = son_arizalar_list
    
    # Excel'deki TOPLAM arıza sayısı - Proje-dinamik
    from flask import current_app
    current_project = session.get('current_project', 'belgrad')
    ariza_dir = os.path.join(current_app.root_path, 'logs', current_project, 'ariza_listesi')
    
    # Arıza Listesi dosyasını bul
    ariza_listesi_file = None
    if os.path.exists(ariza_dir):
        for file in os.listdir(ariza_dir):
            if file.endswith('.xlsx') and not file.startswith('~$'):
                ariza_listesi_file = os.path.join(ariza_dir, file)
                break
    
    total_failures_last_30_days = 0
    if ariza_listesi_file:
        try:
            # Header row'u belirle - logs klasöründe ise 3, yoksa 0
            header_row = 3 if 'logs' in ariza_listesi_file and 'ariza_listesi' in ariza_listesi_file else 0
            df_for_count = pd.read_excel(ariza_listesi_file, sheet_name='FRACAS', header=header_row)
            # Tüm arıza sayısı (filtreleme yok, sadece excel'deki tüm)
            total_failures_last_30_days = len(df_for_count)
        except Exception as e:
            logger.error(f'Total failures count error: {e}')
            total_failures_last_30_days = len(son_arizalar_list)
    
    # Arıza sınıflarına göre sayı hesapla
    ariza_by_class = get_ariza_counts_by_class()
    
    # Filo durumu istatistikleri - Servis durumundan hesapla
    aktif_count = 0
    ariza_count = 0
    bakim_count = 0
    
    for tramvay_status in tramvay_statuses:
        if tramvay_status['status'] == 'aktif':
            aktif_count += 1
        elif 'warning' in tramvay_status['status_color']:
            bakim_count += 1
        else:
            ariza_count += 1
    
    # MTTR (Mean Time To Repair) hesapla - Ortalama Tamir Süresi
    mttr_data = calculate_fleet_mttr()
    
    # Filo Kullanılabilirlik Oranı = (Aktif + Bakımda) / Toplam * 100
    # Servis dışı = sadece arızalı tramvaylar
    total_tram = len(tramvay_statuses)
    kullanilabilir = aktif_count + bakim_count
    fleet_availability = round(kullanilabilir / total_tram * 100, 1) if total_tram > 0 else 0
    
    stats = {
        'total_tramvay': len(tramvay_statuses),
        'aktif_servis': aktif_count,
        'bakimda': bakim_count,
        'arizali': ariza_count,
        'fleet_availability': fleet_availability,
        'aktif_ariza': len(son_arizalar),
        'bekleyen_is_emri': wo_summary.get('pending', 0),
        'devam_eden_is_emri': wo_summary.get('in_progress', 0),
        'mttr': mttr_data,  # MTTR verisi - Ortalama Tamir Süresi
    }
    
    return render_template('dashboard.html',
                         equipment_summary=equipment_summary,
                         wo_summary=wo_summary,
                         critical_work_orders=critical_work_orders,
                         upcoming_maintenance=upcoming_maintenance,
                         recent_failures=recent_failures,
                         latest_kpi=latest_kpi,
                         tramvaylar=tramvay_statuses,
                         son_arizalar=son_arizalar,
                         stats=stats,
                         kpi=latest_kpi,
                         total_failures_last_30_days=total_failures_last_30_days,
                         ariza_sinif_counts=ariza_by_class)


@bp.route('/api/equipment-status')
@login_required
def equipment_status_api():
    """Ekipman durumu grafiği için API"""
    stats = db.session.query(
        Equipment.status,
        func.count(Equipment.id)
    ).filter_by(parent_id=None).group_by(Equipment.status).all()
    
    data = {
        'labels': [status for status, _ in stats],
        'values': [count for _, count in stats]
    }
    
    return jsonify(data)


@bp.route('/api/work-order-trend')
@login_required
def work_order_trend_api():
    """İş emri trend grafiği için API"""
    # Son 12 ay
    data = []
    for i in range(12):
        month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        count = WorkOrder.query.filter(
            WorkOrder.created_at >= month_start,
            WorkOrder.created_at < month_end
        ).count()
        
        data.append({
            'month': month_start.strftime('%Y-%m'),
            'count': count
        })
    
    return jsonify(data[::-1])  # Ters çevir (eskiden yeniye)


@bp.route('/api/failures')
@bp.route('/api/failures/<equipment_code>')
@login_required
def get_equipment_failures(equipment_code=None):
    """Araçla ilgili son 5 arızayı Al - Fracas_BELGRAD.xlsx'den (birleştirilmiş)
    Eğer equipment_code yoksa TÜM son 5 arızayı getir"""
    try:
        import pandas as pd
        import os
        
        # Fracas_BELGRAD.xlsx'i kullan (birleştirilmiş veri kaynağı)
        current_project = session.get('current_project', 'belgrad')
        ariza_listesi_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', current_project, 'ariza_listesi')
        
        # Fracas_*.xlsx ara (birincil)
        ariza_listesi_file = None
        for file in os.listdir(ariza_listesi_dir) if os.path.exists(ariza_listesi_dir) else []:
            if file.upper().startswith('FRACAS_') and file.endswith('.xlsx') and not file.startswith('~$'):
                ariza_listesi_file = os.path.join(ariza_listesi_dir, file)
                break
        
        failures = []
        
        if not ariza_listesi_file or not os.path.exists(ariza_listesi_file):
            logger.error(f'[API] Fracas dosyasi bulunamadi')
            return jsonify({'failures': [], 'error': 'Fracas file not found'})
        
        try:
            # Sheet adını dinamik olarak bul
            sheet_names = pd.ExcelFile(ariza_listesi_file).sheet_names
            logger.info(f'[API] Mevcut Sheet adları: {sheet_names}')
            
            # FRACAS sheet'i ara, yoksa ilk sheet'i kullan
            sheet_to_use = None
            if 'FRACAS' in sheet_names:
                sheet_to_use = 'FRACAS'
            elif sheet_names:
                sheet_to_use = sheet_names[0]
            else:
                return jsonify({'failures': [], 'error': 'No sheets found in Excel file'})
            
            logger.info(f'[API] Kullanılan sheet: {sheet_to_use}')
            
            # Header satırını dinamik olarak bul (varsayılan: 3, yani 4. satırdan başla)
            df = pd.read_excel(ariza_listesi_file, sheet_name=sheet_to_use, header=3)
            logger.info(f'[API] Excel okundu - {len(df)} satir, Sutunlar: {list(df.columns)[:5]}...')
            
            # FRACAS ID sütununu doğrula
            if not any('FRACAS' in str(col).upper() and 'ID' in str(col).upper() for col in df.columns):
                logger.error('[API] FRACAS ID sutunu bulunamadi')
                return jsonify({'failures': [], 'error': 'FRACAS ID column not found'})
            
            # FRACAS ID sütunu bul (farklı adlar olabilir)
            fracas_id_col = None
            for col in df.columns:
                if 'FRACAS' in str(col).upper() and 'ID' in str(col).upper():
                    fracas_id_col = col
                    break
            
            # Araç No sütununu bul (farklı adlar olabilir)
            arac_no_col = None
            for col in df.columns:
                if 'araç' in str(col).lower() and ('no' in str(col).lower() or 'numarası' in str(col).lower()):
                    arac_no_col = col
                    break
            
            # Eğer equipment_code verildiyse filtrele, değilse son 5'i getir
            if equipment_code and equipment_code.strip():
                # TRN- prefix'ini kaldır (eğer varsa)
                equipment_code_clean = equipment_code.replace('TRN-', '').strip()
                
                if arac_no_col:
                    # Araç numarasını normalize et (float da olabilir)
                    try:
                        # Float olarak deneyerek normalleştir
                        equipment_code_float = float(equipment_code_clean)
                        equipment_code_normalized = str(int(equipment_code_float))
                        
                        # DataFrame'deki araç no'larını da normalize et
                        arac_no_series = df[arac_no_col].astype(str).str.strip()
                        # Float parse et
                        arac_no_normalized = arac_no_series.apply(lambda x: str(int(float(x))) if x and x != '-' else x)
                        
                        filtered_df = df[arac_no_normalized == equipment_code_normalized]
                    except (ValueError, TypeError):
                        # String karşılaştırması yap
                        filtered_df = df[df[arac_no_col].astype(str).str.strip() == str(equipment_code_clean).strip()]
                    
                    filtered_df = filtered_df.tail(5)
                else:
                    filtered_df = df.tail(5)
            else:
                # Boş satırları hariç tut, son 5'i getir
                filtered_df = df[df[fracas_id_col].notna()].tail(5) if fracas_id_col else df.tail(5)
            
            logger.debug(f'[API] Filtrelenen satir sayisi: {len(filtered_df)}')
            
            # Sütunları hazırla
            for idx, row in filtered_df.iterrows():
                try:
                    # Pandas Series olarak erişim, sütun adlarını dinamik ara
                    fracas_id = str(row[fracas_id_col]).strip() if fracas_id_col and pd.notna(row[fracas_id_col]) else ''
                    
                    # Araç no'yu normalize et (1547.0 → 1547)
                    arac_no_raw = str(row[arac_no_col]).strip() if arac_no_col and pd.notna(row[arac_no_col]) else ''
                    try:
                        arac_no_float = float(arac_no_raw)
                        arac_no = str(int(arac_no_float))
                    except (ValueError, TypeError):
                        arac_no = arac_no_raw
                    
                    # Sistem sütunu ara
                    sistem_col = next((col for col in df.columns if 'sistem' in str(col).lower()), None)
                    sistem = str(row[sistem_col]).strip() if sistem_col and pd.notna(row[sistem_col]) else ''
                    
                    # Arıza Tanımı sütunu ara
                    ariza_def_col = next((col for col in df.columns if 'arıza' in str(col).lower() and 'tanım' in str(col).lower()), None)
                    ariza_tanimi = str(row[ariza_def_col]).strip() if ariza_def_col and pd.notna(row[ariza_def_col]) else ''
                    
                    # Tarih sütunu ara
                    tarih_col = next((col for col in df.columns if 'tarih' in str(col).lower()), None)
                    tarih = str(row[tarih_col]).strip() if tarih_col and pd.notna(row[tarih_col]) else ''
                    
                    # Durum sütunu ara
                    durum_col = next((col for col in df.columns if 'durum' in str(col).lower()), None)
                    durum = str(row[durum_col]).strip() if durum_col and pd.notna(row[durum_col]) else ''
                    
                    failures.append({
                        'fracas_id': fracas_id,
                        'arac_no': arac_no,
                        'sistem': sistem,
                        'ariza_tanimi': ariza_tanimi,
                        'tarih': tarih,
                        'durum': durum
                    })
                    logger.debug(f'[API] Satir {idx}: {fracas_id} - {arac_no}')
                except Exception as e:
                    logger.error(f'[API] Satir {idx} isleme hatasi: {e}')
                    continue
            
            logger.info(f'[API] Toplam {len(failures)} ariza donduruluyorr')
            return jsonify({'failures': failures, 'count': len(failures)})
            
        except Exception as excel_error:
            logger.error(f'[API] Excel okuma hatasi: {type(excel_error).__name__}: {excel_error}')
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'failures': [], 'error': f'Excel read error: {str(excel_error)}'})
    
    except Exception as e:
        logger.error(f'[API] Genel hata: {type(e).__name__}: {e}')
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'failures': [], 'error': f'General error: {str(e)}'})

