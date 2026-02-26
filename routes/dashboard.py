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


def sync_excel_to_equipment(project_code=None):
    """Excel'den okunan araçları Equipment table'a senkronize et (OTOMATIK)
    
    - Excel'deki tüm araçları bul
    - Equipment'ta olmayan araçları ekle
    - Dinamik Excel update'lerine destek sağla
    """
    if project_code is None:
        project_code = session.get('current_project', 'belgrad')
    
    veriler_file = ProjectManager.get_veriler_file(project_code)
    if not veriler_file or not os.path.exists(veriler_file):
        return []
    
    try:
        df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
        
        # Excel'deki tram_id'leri al
        if 'tram_id' in df.columns:
            excel_trams = sorted([str(t) for t in df['tram_id'].dropna().unique().tolist()])
        elif 'equipment_code' in df.columns:
            excel_trams = sorted([str(c) for c in df['equipment_code'].dropna().unique().tolist()])
        else:
            return []
        
        # Equipment'ta olmayanları bul
        existing_eqs = Equipment.query.filter_by(parent_id=None, project_code=project_code).all()
        existing_codes = set(eq.equipment_code for eq in existing_eqs)
        excel_codes = set(excel_trams)
        
        missing = excel_codes - existing_codes
        
        # Eksik araçları ekle
        if missing:
            template = existing_eqs[0] if existing_eqs else None
            if template:
                for tram_id in sorted(missing):
                    new_eq = Equipment(
                        equipment_code=tram_id,
                        name=f'Tramvay {tram_id}',
                        project_code=project_code,
                        parent_id=None,
                        status='aktif',
                        location=getattr(template, 'location', None),  # Template'dan location'ı kopyala
                        criticality=getattr(template, 'criticality', 'medium'),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(new_eq)
                
                db.session.commit()
                logger.info(f'[AUTO-SYNC] {len(missing)} araç eklendi ({project_code}): {sorted(missing)}')
        
        return excel_trams
    
    except Exception as e:
        logger.error(f'Auto-sync hatası ({project_code}): {e}')
        # Fallback: Equipment'tan çek
        return [eq.equipment_code for eq in Equipment.query.filter_by(parent_id=None, project_code=project_code).all()]


def get_tram_ids_from_veriler(project_code=None):
    """Veriler.xlsx'den equipment_code'leri yükle - OTOMATIK SYNC İLE - Proje bazlı"""
    if project_code is None:
        project_code = session.get('current_project', 'belgrad')
    
    # OTOMATIK SYNC: Excel'i oku, Equipment'a eksik olanları ekle
    excel_trams = sync_excel_to_equipment(project_code)
    return excel_trams

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.after_request
def disable_cache_on_dashboard(response):
    """Dashboard sayfasının cache'lenememesi için - Her refresh'de fresh veri çeksin"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


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
        WorkOrder.status.in_(['pending', 'scheduled', 'in_progress']),
        WorkOrder.project_code == current_project
    ).order_by(WorkOrder.planned_start).limit(10).all()
    
    # Yaklaşan bakımlar (7 gün içinde)
    upcoming_maintenance = WorkOrder.query.filter(
        WorkOrder.status.in_(['pending', 'scheduled']),
        WorkOrder.planned_start >= datetime.utcnow(),
        WorkOrder.planned_start <= datetime.utcnow() + timedelta(days=7),
        WorkOrder.project_code == current_project
    ).order_by(WorkOrder.planned_start).limit(10).all()
    
    # Son arızalar - Excel'den çek
    recent_failures, ariza_sinif_counts = get_failures_from_excel()
    
    # Son KPI'lar
    latest_kpi = KPISnapshot.query.order_by(
        KPISnapshot.snapshot_date.desc()
    ).first()
    
    # ===== Tramvay Filosu - Veriler.xlsx'ten tram_id'leri oku (proje-dinamik) =====
    # Veriler.xlsx'ten tram_id listesini al
    tram_ids_from_excel = get_tram_ids_from_veriler(current_project)
    
    tramvaylar = []
    if tram_ids_from_excel:
        # Excel'den okunan tram_id'lere göre tramvayları filtrele
        tramvaylar = Equipment.query.filter(
            Equipment.equipment_code.in_(tram_ids_from_excel),
            Equipment.parent_id.is_(None),
            Equipment.project_code == current_project
        ).order_by(Equipment.equipment_code).all()
        logger.debug(f'[DASHBOARD] Found {len(tramvaylar)} trams from Veriler.xlsx ({current_project})')
    
    # Eğer Excel'den bulunamazsa fallback
    if not tramvaylar:
        logger.debug(f'[DASHBOARD FALLBACK] No trams from Veriler.xlsx, using all project equipment')
        tramvaylar = Equipment.query.filter_by(
            parent_id=None,
            project_code=current_project
        ).order_by(Equipment.equipment_code).all()
        logger.debug(f'[DASHBOARD FALLBACK] Found {len(tramvaylar)} trams')
    
    # Bugünün tarihi
    today = str(date.today())
    
    # Her tramvay için ServiceStatus'ten durum al
    tramvay_statuses = []
    for tramvay in tramvaylar:
        # PRIMARY: ServiceStatus'ten bugün'ün kaydını al
        service_record = ServiceStatus.query.filter_by(
            tram_id=tramvay.equipment_code,
            date=today,
            project_code=current_project
        ).first()
        
        # ✓ Auto-create: ServiceStatus kaydı yoksa oluştur
        if not service_record:
            service_record = ServiceStatus(
                tram_id=tramvay.equipment_code,
                date=today,
                project_code=current_project,
                status='İşletme',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(service_record)
            db.session.commit()
        
        # Durum belirle - ServiceStatus PRIMARY source
        status_display = 'aktif'
        status_color = 'success'
        status_from_db = 'Aktif'
        
        # ServiceStatus varsa onu kullan
        if service_record and service_record.status:
            service_status = service_record.status
            
            # ServiceStatus değerine göre çevir
            if 'İşletme' in service_status or 'işletme' in service_status.lower():
                status_display = 'işletme'
                status_color = 'warning'
                status_from_db = 'İşletme Kaynaklı Servis Dışı'
            elif 'Dışı' in service_status or 'disi' in service_status.lower() or 'ariza' in service_status.lower():
                status_display = 'ariza'
                status_color = 'danger'
                status_from_db = 'Servis Dışı'
            else:
                status_display = 'aktif'
                status_color = 'success'
                status_from_db = 'Aktif'
        else:
            # ServiceStatus yoksa default 'aktif'
            status_display = 'aktif'
            status_color = 'success'
            status_from_db = 'Aktif'
        
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
    
    # Arıza sınıflarına göre sayı hesapla
    ariza_by_class = get_ariza_counts_by_class()
    
    # Toplam arıza sayısı = A + B + C + D (arıza_by_class'dan)
    # Bu şekilde her zaman doğru dosyandan veri gelir
    total_failures_last_30_days = sum(cls_data['count'] for cls_data in ariza_by_class.values())
    
    # Log the counts
    logger.debug(f'A={ariza_by_class["A"]["count"]}, B={ariza_by_class["B"]["count"]}, C={ariza_by_class["C"]["count"]}, D={ariza_by_class["D"]["count"]}, TOTAL={total_failures_last_30_days}')
    
    # Filo durumu istatistikleri - ServiceStatus'ten hesapla
    aktif_count = 0
    isletme_count = 0  # İşletme Kaynaklı Servis Dışı
    ariza_count = 0
    
    for tramvay_status in tramvay_statuses:
        if tramvay_status['status'] == 'aktif':
            aktif_count += 1
        elif tramvay_status['status'] == 'işletme':  # İşletme Kaynaklı Servis Dışı
            isletme_count += 1
        else:  # Arızalı
            ariza_count += 1
    
    # MTTR (Mean Time To Repair) hesapla - Ortalama Tamir Süresi
    mttr_data = calculate_fleet_mttr()
    
    # Filo Kullanılabilirlik Oranı = (Aktif + İşletme Kaynaklı) / Toplam * 100
    # Bu ikisinin toplamı çalışabilir araçları temsil eder (İşletme kaynaklı olanlar zamanla servis dönebilir)
    total_tram = len(tramvay_statuses) if tramvay_statuses else 1  # 0'a bölmek için 1 minimum
    kullanilabilir = aktif_count + isletme_count
    fleet_availability = round(kullanilabilir / total_tram * 100, 1) if total_tram > 0 else 0
    
    # Debug logging
    logger.debug(f'[STATS CALC] Total: {total_tram}, Aktif: {aktif_count}, İşletme: {isletme_count}, Arıza: {ariza_count}, Availability: {fleet_availability}%')
    
    stats = {
        'total_tramvay': total_tram,
        'aktif_servis': aktif_count,
        'bakimda': isletme_count,  # İşletme Kaynaklı Servis Dışı
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
    current_project = session.get('current_project', 'belgrad')
    # Son 12 ay
    data = []
    for i in range(12):
        month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        count = WorkOrder.query.filter(
            WorkOrder.created_at >= month_start,
            WorkOrder.created_at < month_end,
            WorkOrder.project_code == current_project
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
    """Araçla ilgili son arızaları al - Excel'den (data/{proje}/Veriler.xlsx)"""
    try:
        import pandas as pd
        import os
        
        current_project = session.get('current_project', 'belgrad')
        
        # Excel'den arızaları oku
        veriler_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', current_project, 'Veriler.xlsx')
        
        if not os.path.exists(veriler_file):
            logger.error(f'[API] {veriler_file} bulunamadi')
            return jsonify({'failures': [], 'error': 'Veriler file not found'})
        
        try:
            df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
            logger.info(f'[API] Excel okundu - {len(df)} satir, sutunlar: {list(df.columns)}')
            
            # Arıza sütununu bul
            ariza_col = None
            for col in df.columns:
                if 'arız' in col.lower() or 'class' in col.lower():
                    ariza_col = col
                    break
            
            # Önce arıza dolu satırları filtrele
            if ariza_col:
                filtered_df = df[df[ariza_col].notna()]
                filtered_df = filtered_df[filtered_df[ariza_col] != '']
                filtered_df = filtered_df[filtered_df[ariza_col] != 'nan']
                logger.info(f'[API] Arıza dolu satırlar: {len(filtered_df)}')
            else:
                filtered_df = df
            
            # Equipment code verilirse filtrele
            if equipment_code:
                equipment_code = equipment_code.strip().replace('TRN-', '')
                logger.info(f'[API] Filtre: {equipment_code}')
                
                # tram_id kolonunu bul ve normal et (1547.0 -> 1547)
                tram_id_col = None
                for col in df.columns:
                    if 'tram' in col.lower() and 'id' in col.lower():
                        tram_id_col = col
                        break
                
                if tram_id_col:
                    # String'e çevir ve normalize et
                    filtered_df[tram_id_col] = filtered_df[tram_id_col].astype(str).str.strip()
                    filtered_df[tram_id_col] = filtered_df[tram_id_col].apply(
                        lambda x: str(int(float(x))) if x.replace('.', '').isdigit() else x
                    )
                    filtered_df = filtered_df[filtered_df[tram_id_col] == equipment_code]
                    logger.info(f'[API] {equipment_code} için {len(filtered_df)} arıza bulundu')
            
            # Son 5 arızayı al (arıza dolu satırlardan)
            filtered_df = filtered_df.tail(5)
            
            failures = []
            for idx, row in filtered_df.iterrows():
                try:
                    # Sütunları bul - flexible column names
                    tram_id = str(row.get('tram_id', '')).strip()
                    if not tram_id:
                        # Alternatif isimler
                        for col in ['Tramvay ID', 'Araç No', 'Araç Kodu', 'Vehicle ID']:
                            if col in row.index:
                                tram_id = str(row.get(col, '')).strip()
                                break
                    
                    # tram_id'yi normalize et (1547.0 -> 1547)
                    if tram_id and tram_id != 'nan':
                        try:
                            tram_id = str(int(float(tram_id)))
                        except:
                            pass
                    
                    # Module/Sistem
                    module = None
                    for col in ['Module', 'Sistem', 'System', 'sistem']:
                        if col in row.index:
                            module = str(row.get(col, '')).strip()
                            if module != 'nan' and module:
                                break
                    if not module:
                        module = 'Bilinmiyor'
                    
                    # Arıza Sınıfı
                    ariza_sinifi = None
                    for col in ['Arıza Sınıfı ', 'Arıza Sınıfı', 'Failure Class', 'ariza_sinifi']:
                        if col in row.index:
                            ariza_sinifi = str(row.get(col, '')).strip()
                            if ariza_sinifi != 'nan' and ariza_sinifi:
                                break
                    
                    # NaN değerleri filtrele
                    if not ariza_sinifi or ariza_sinifi == 'nan':
                        continue
                    
                    # Arıza Kaynağı ve Tipi (isteğe bağlı)
                    ariza_kaynagi = str(row.get('Arıza Kaynağı', '')).strip() if 'Arıza Kaynağı' in row.index else ''
                    ariza_tipi = str(row.get('Arıza Tipi', '')).strip() if 'Arıza Tipi' in row.index else ''
                    
                    failures.append({
                        'fracas_id': tram_id,
                        'arac_no': tram_id,
                        'sistem': module,
                        'ariza_tanimi': ariza_sinifi,
                        'tarih': '',
                        'durum': f'{ariza_kaynagi} | {ariza_tipi}' if ariza_kaynagi else ariza_tipi
                    })
                except Exception as e:
                    logger.warning(f'[API] Satır işleme uyarısı: {e}')
                    continue
            
            logger.info(f'[API] {len(failures)} arıza donduruldu')
            return jsonify({'failures': failures, 'count': len(failures)})
            
        except Exception as excel_error:
            logger.error(f'[API] Excel okuma hatası: {excel_error}')
            return jsonify({'failures': [], 'error': str(excel_error)})
    
    except Exception as e:
        logger.error(f'[API] Genel hata: {type(e).__name__}: {e}')
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'failures': [], 'error': f'General error: {str(e)}'})

