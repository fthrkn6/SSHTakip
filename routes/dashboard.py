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
            # Project-specific FRACAS dosyasını ara (örn: Fracas_BELGRAD.xlsx)
            project_file_map = {
                'belgrad': 'Fracas_BELGRAD.xlsx',
                'gebze': 'Fracas_GEBZE.xlsx',
                'iasi': 'Fracas_IASI.xlsx',
                'kayseri': 'Fracas_KAYSERİ.xlsx',
                'kocaeli': 'Fracas_KOCAELI.xlsx',
                'timisoara': 'Fracas_TIMISOARA.xlsx'
            }
            
            specific_fracas = project_file_map.get(current_project)
            if specific_fracas:
                test_file = os.path.join(ariza_dir, specific_fracas)
                if os.path.exists(test_file):
                    ariza_listesi_file = test_file
            
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
    
    Veri Kaynağı: FRACAS.xlsx AB sütunu (Komponent MTTR)
    """
    from flask import current_app
    import re
    
    try:
        current_project = session.get('current_project', 'belgrad')
        
        # FRACAS dosyasını bul
        data_dir = os.path.join(current_app.root_path, 'data', current_project)
        fracas_file = None
        
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.lower().startswith('fracas') and file.endswith('.xlsx'):
                    fracas_file = os.path.join(data_dir, file)
                    break
        
        mttr_minutes = 0
        total_failures = 0
        total_repair_time = 0
        
        if fracas_file:
            try:
                # FRACAS Excel'inin FRACAS sheet'ini oku (header=3, yani 4. satır)
                df = pd.read_excel(fracas_file, sheet_name='FRACAS', header=3)
                
                # AB sütununu ara (Komponent MTTR)
                komponent_mttr_col = None
                for col in df.columns:
                    if 'komponent' in col.lower() and 'mttr' in col.lower():
                        komponent_mttr_col = col
                        break
                
                # Eğer Komponent MTTR sütunu varsa, topla ve hesapla
                if komponent_mttr_col:
                    mttr_values = []
                    
                    for val in df[komponent_mttr_col].dropna():
                        try:
                            # Değer numero olabilir direkt
                            if isinstance(val, (int, float)):
                                mttr_values.append(float(val))
                            else:
                                val_str = str(val).strip()
                                # "180", "180 dk" gibi formatları destekle
                                match = re.search(r'(\d+(?:[\.,]\d+)?)', val_str)
                                if match:
                                    number_str = match.group(1).replace(',', '.')
                                    mttr_values.append(float(number_str))
                        except:
                            continue
                    
                    if len(mttr_values) > 0:
                        total_repair_time = sum(mttr_values)
                        total_failures = len(mttr_values)
                        mttr_minutes = total_repair_time / total_failures  # Formül: Toplam Tamir Süresi / Arıza Sayısı
                        mttr_minutes = round(mttr_minutes, 1)
                        logger.debug(f'[MTTR DEBUG] Toplam Tamir Süresi: {total_repair_time} dk, Arıza Sayısı: {total_failures}, MTTR: {mttr_minutes} dk')
                    else:
                        logger.debug(f'[MTTR DEBUG] FRACAS dosyasında Komponent MTTR değeri bulunamadi')
                else:
                    logger.debug(f'[MTTR DEBUG] AB (Komponent MTTR) sutunu bulunamadi')
            
            except Exception as e:
                logger.error(f'[MTTR DEBUG] FRACAS MTTR okuma hatasi: {e}')
                import traceback
                logger.error(traceback.format_exc())
                total_failures = 0
                mttr_minutes = 0
        
        # Dakikayı saat:dakika formatına dönüştür
        hours = int(mttr_minutes // 60) if mttr_minutes > 0 else 0
        minutes = int(mttr_minutes % 60) if mttr_minutes > 0 else 0
        mttr_formatted = f"{int(mttr_minutes)} dk" if mttr_minutes > 0 else "0 dk"
        
        logger.debug(f'[MTTR FINAL] Proje:{current_project}, Toplam Tamir Süresi:{total_repair_time} dk, Arıza Sayısı:{total_failures}, MTTR:{mttr_minutes} dk')
        
        return {
            'mttr_minutes': mttr_minutes,
            'mttr_formatted': mttr_formatted,
            'mttr_hours': round(mttr_minutes / 60, 1),
            'total_failures': total_failures,
            'total_repair_time': total_repair_time,
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
    
    # Toplam arızaları getir - FRACAS dosyasından gerçek veriler
    try:
        import pandas as pd
        current_project = session.get('current_project', 'belgrad')
        ariza_listesi_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', current_project, 'ariza_listesi')
        
        ariza_listesi_file = None
        use_sheet = None
        
        if os.path.exists(ariza_listesi_dir):
            # Project-specific FRACAS dosyasını ara (örn: Fracas_BELGRAD.xlsx)
            project_file_map = {
                'belgrad': 'Fracas_BELGRAD.xlsx',
                'gebze': 'Fracas_GEBZE.xlsx',
                'iasi': 'Fracas_IASI.xlsx',
                'kayseri': 'Fracas_KAYSERİ.xlsx',
                'kocaeli': 'Fracas_KOCAELI.xlsx',
                'timisoara': 'Fracas_TIMISOARA.xlsx'
            }
            
            specific_fracas = project_file_map.get(current_project)
            if specific_fracas:
                specific_path = os.path.join(ariza_listesi_dir, specific_fracas)
                if os.path.exists(specific_path):
                    ariza_listesi_file = specific_path
                    use_sheet = 'FRACAS'
            
            # Fallback: varsa başka Fracas_*.xlsx
            if not ariza_listesi_file:
                for file in os.listdir(ariza_listesi_dir):
                    if file.upper().startswith('FRACAS_') and file.endswith('.xlsx') and not file.startswith('~$'):
                        ariza_listesi_file = os.path.join(ariza_listesi_dir, file)
                        use_sheet = 'FRACAS'
                        break
        
        son_arizalar_list = []
        if ariza_listesi_file and os.path.exists(ariza_listesi_file):
            try:
                df = pd.read_excel(ariza_listesi_file, sheet_name=use_sheet, header=3)
                
                # Sütunları bul
                tram_col = None
                ariza_col = None
                sistem_col = None
                
                for col in df.columns:
                    if 'araç' in col.lower() and 'numarası' in col.lower() and not tram_col:
                        tram_col = col
                    if 'arıza tanımı' in col.lower() and not ariza_col:
                        ariza_col = col
                    if col.lower().strip() == 'sistem' and not sistem_col:
                        sistem_col = col
                
                if tram_col and ariza_col:
                    # Arıza dolu satırları filtrele
                    df_filtered = df[df[ariza_col].notna()]
                    df_filtered = df_filtered[df_filtered[ariza_col].astype(str) != '']
                    df_filtered = df_filtered[df_filtered[ariza_col].astype(str) != 'nan']
                    
                    # Son 5'ini al
                    for idx, row in df_filtered.tail(5).iterrows():
                        tram_id = str(row.get(tram_col, 'N/A')).strip()
                        try:
                            tram_id = str(int(float(tram_id)))
                        except:
                            pass
                        
                        sistem = str(row.get(sistem_col, 'N/A')).strip() if sistem_col else 'N/A'
                        ariza = str(row.get(ariza_col, 'N/A')).strip()
                        
                        son_arizalar_list.append({
                            'fracas_id': tram_id,
                            'arac_no': tram_id,
                            'sistem': sistem,
                            'ariza_tanimi': ariza,
                            'tarih': '',
                        })
            except Exception as e:
                logger.warning(f'[Dashboard] FRACAS okuma hatası: {e}')
    except Exception as e:
        logger.warning(f'[Dashboard] Arıza yükleme hatası: {e}')
    
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
    """Araçla ilgili son arızaları al - Arıza Listesi sources'tan (FRACAS veya Veriler.xlsx)"""
    try:
        import pandas as pd
        import os
        import glob
        
        current_project = session.get('current_project', 'belgrad')
        print(f"[DEBUG-API] current_project from session: {current_project}", flush=True)
        print(f"[DEBUG-API] equipment_code: {equipment_code}", flush=True)
        
        # Birincil konum: logs/{project}/ariza_listesi/
        ariza_listesi_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', current_project, 'ariza_listesi')
        
        ariza_listesi_file = None
        use_sheet = None
        header_row = 0
        
        print(f"[DEBUG-API] Arizing_listesi_dir: {ariza_listesi_dir}", flush=True)
        print(f"[DEBUG-API] Dir exists: {os.path.exists(ariza_listesi_dir)}", flush=True)
        
        if os.path.exists(ariza_listesi_dir):
            # Tüm Fracas_*.xlsx dosyalarını ara (Türkçe karakterleri ignore et)
            fracas_files = glob.glob(os.path.join(ariza_listesi_dir, 'Fracas_*.xlsx'))
            fracas_files = [f for f in fracas_files if not f.startswith('~$')]
            
            print(f"[DEBUG-API] Bulunan Fracas dosyaları: {fracas_files}", flush=True)
            
            if fracas_files:
                ariza_listesi_file = fracas_files[0]
                use_sheet = 'FRACAS'
                header_row = 3
                print(f"[DEBUG-API] Seçilen Fracas dosyası: {ariza_listesi_file}", flush=True)
        
        # Fallback: Ariza_Listesi dosyası
        if not ariza_listesi_file and os.path.exists(ariza_listesi_dir):
            for file in os.listdir(ariza_listesi_dir):
                if 'Ariza_Listesi' in file and file.endswith('.xlsx') and not file.startswith('~$'):
                    ariza_listesi_file = os.path.join(ariza_listesi_dir, file)
                    use_sheet = 'Ariza Listesi'
                    header_row = 3
                    print(f"[DEBUG-API] Fallback Ariza_Listesi kullanılıyor: {ariza_listesi_file}", flush=True)
                    break
        
        # Fallback: data/{project}/Veriler.xlsx (Sayfa2)
        if not ariza_listesi_file:
            veriler_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', current_project, 'Veriler.xlsx')
            if os.path.exists(veriler_file):
                ariza_listesi_file = veriler_file
                use_sheet = 'Sayfa2'
                header_row = 0
                print(f"[DEBUG-API] Fallback Veriler.xlsx kullanılıyor: {ariza_listesi_file}", flush=True)
        
        if not ariza_listesi_file or not os.path.exists(ariza_listesi_file):
            logger.warning(f'[API] Arıza kaynağı bulunamadı: {current_project}')
            print(f"[DEBUG-API] ✗ Arıza kaynağı bulunamadı!", flush=True)
            return jsonify({'failures': [], 'count': 0, 'error': 'Arıza kaynağı bulunamadı'})
        
        print(f"[DEBUG-API] Kullanılan dosya: {ariza_listesi_file}, Sheet: {use_sheet}", flush=True)
        
        try:
            # Excel'i oku
            df = pd.read_excel(ariza_listesi_file, sheet_name=use_sheet, header=header_row)
            logger.info(f'[API] {ariza_listesi_file} okundu - {len(df)} satır, sütunlar: {list(df.columns)[:5]}...')
            print(f"[DEBUG-API] Excel okundu: {len(df)} satır", flush=True)
            print(f"[DEBUG-API] TÜM SÜTUN ADLARI: {list(df.columns)}", flush=True)
            
            # Sütunları bul - flexible names
            tram_id_col = None
            for col in df.columns:
                if 'araç' in col.lower() and 'numarası' in col.lower():  # FRACAS format
                    tram_id_col = col
                    break
                if 'tram' in col.lower() and 'id' in col.lower():  # Fallback
                    tram_id_col = col
                    break
            
            ariza_col = None
            for col in df.columns:
                if 'arıza sınıfı' in col.lower():  # FRACAS format
                    ariza_col = col
                    break
                if 'arıza tanımı' in col.lower():  # FRACAS format
                    ariza_col = col
                    break
                if 'arız' in col.lower() or ('failure' in col.lower() and 'class' in col.lower()):
                    ariza_col = col
                    break
            
            sistem_col = None
            for col in df.columns:
                if col.lower().strip() == 'sistem':  # Exact match
                    sistem_col = col
                    break
                if 'alt sistem' in col.lower():  # FRACAS fallback
                    sistem_col = col
                    break
                if 'module' in col.lower():
                    sistem_col = col
                    break
            
            print(f"[DEBUG-API] Tüm sütunlar: {list(df.columns)}", flush=True)
            print(f"[DEBUG-API] Sütunlar - tram_id: {tram_id_col}, ariza: {ariza_col}, sistem: {sistem_col}", flush=True)
            
            if not tram_id_col or not ariza_col:
                logger.warning(f'[API] Gerekli sütunlar bulunamadı. tram_id: {tram_id_col}, ariza: {ariza_col}')
                print(f"[DEBUG-API] ✗ Gerekli sütunlar bulunamadı!", flush=True)
                return jsonify({'failures': [], 'count': 0, 'error': 'Sütun eşleştirmesi yapılamadı'})
            
            # Arıza dolu satırları filtrele
            filtered_df = df[df[ariza_col].notna()]
            filtered_df = filtered_df[filtered_df[ariza_col] != '']
            
            # NaN/nan stringini filtrele
            filtered_df = filtered_df[filtered_df[ariza_col].astype(str) != 'nan']
            
            logger.info(f'[API] Arıza dolu satırlar: {len(filtered_df)}')
            print(f"[DEBUG-API] Arıza dolu satırlar: {len(filtered_df)}", flush=True)
            
            # Equipment code verilirse filtrele
            if equipment_code:
                equipment_code = equipment_code.strip().replace('TRN-', '')
                print(f"[DEBUG-API] Equipment code normalize: {equipment_code}", flush=True)
                
                # tram_id'yi normalize et
                filtered_df[tram_id_col] = filtered_df[tram_id_col].astype(str).str.strip()
                print(f"[DEBUG-API] Normalize ÖNCESİ sütun örnekleri: {filtered_df[tram_id_col].head().tolist()}", flush=True)
                
                # Paranthesli kodları temizle: '3874(3)' → '3874'
                import re
                filtered_df[tram_id_col] = filtered_df[tram_id_col].apply(
                    lambda x: re.sub(r'\(\d+\)$', '', str(x)).strip() if pd.notna(x) else x
                )
                
                # Sayısal normalize: '3874.0' → '3874'
                filtered_df[tram_id_col] = filtered_df[tram_id_col].apply(
                    lambda x: str(int(float(x))) if x.replace('.', '').replace('-', '').isdigit() else x
                )
                
                print(f"[DEBUG-API] Normalize SONRASI sütun örnekleri: {filtered_df[tram_id_col].head().tolist()}", flush=True)
                print(f"[DEBUG-API] Aranıyor: '{equipment_code}' - Sütundaki tüm değerler: {filtered_df[tram_id_col].unique()[:20]}", flush=True)
                
                filtered_df = filtered_df[filtered_df[tram_id_col] == equipment_code]
                logger.info(f'[API] {equipment_code} aracı: {len(filtered_df)} arıza')
                print(f"[DEBUG-API] {equipment_code} aracı filtresi: {len(filtered_df)} arıza", flush=True)
                if len(filtered_df) == 0:
                    print(f"[DEBUG-API] ⚠️ Sonuç 0! Eşleştirme başarısız.", flush=True)
            
            # Son 5 arızayı al
            if len(filtered_df) > 5:
                filtered_df = filtered_df.iloc[-5:]
            
            failures = []
            for idx, row in filtered_df.iterrows():
                try:
                    tram_id = str(row.get(tram_id_col, '')).strip()
                    
                    # tram_id'yi normalize et (1547.0 -> 1547)
                    if tram_id and tram_id != 'nan':
                        try:
                            tram_id = str(int(float(tram_id)))
                        except:
                            pass
                    
                    # Sistem/Module
                    sistem = 'Bilinmiyor'
                    if sistem_col:
                        sistem = str(row.get(sistem_col, 'Bilinmiyor')).strip()
                        if not sistem or sistem == 'nan':
                            sistem = 'Bilinmiyor'
                    
                    # Arıza Sınıfı
                    ariza_sinifi = str(row.get(ariza_col, '')).strip()
                    
                    failures.append({
                        'fracas_id': tram_id,
                        'arac_no': tram_id,
                        'sistem': sistem,
                        'ariza_tanimi': ariza_sinifi,
                        'tarih': '',
                    })
                except Exception as e:
                    logger.warning(f'[API] Satır işleme uyarısı: {e}')
                    continue
            
            logger.info(f'[API] {len(failures)} arıza döndürülüyor')
            print(f"[DEBUG-API] ✓ {len(failures)} arıza gönderiliyor", flush=True)
            return jsonify({'failures': failures, 'count': len(failures)})
            
        except Exception as excel_error:
            logger.error(f'[API] Excel okuma hatası: {excel_error}')
            print(f"[DEBUG-API] ✗ Excel okuma hatası: {excel_error}", flush=True)
            return jsonify({'failures': [], 'error': str(excel_error)})
    
    except Exception as e:
        logger.error(f'[API] Hata: {type(e).__name__}: {e}')
        import traceback
        logger.error(traceback.format_exc())
        print(f"[DEBUG-API] ✗ API Hatası: {e}", flush=True)
        return jsonify({'failures': [], 'error': f'API Error: {str(e)}'})

