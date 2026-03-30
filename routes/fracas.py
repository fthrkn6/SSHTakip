"""
FRACAS (Failure Reporting, Analysis and Corrective Action System) Analiz Modülü
Raylı Sistemler için EN 50126 RAMS Standartlarına Uygun Analizler
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app, session
from flask_login import login_required, current_user
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import logging
import sys
from utils.project_manager import ProjectManager
from utils_performance import CacheConfig
from utils.backup_manager import BackupManager

logger = logging.getLogger(__name__)

bp = Blueprint('fracas', __name__, url_prefix='/fracas')

# Excel sütun eşleştirmeleri (Türkçe -> İngilizce)
COLUMN_MAPPING = {
    'Araç Numarası Vehicle Number': 'vehicle_number',
    'Araç Module Vehicle Module': 'vehicle_module',
    'Araç Kilometresi Vehicle Kilometer': 'vehicle_km',
    'FRACAS ID': 'fracas_id',
    'Hata Tarih /Date': 'failure_date',
    'Hata Saat /Time': 'failure_time',
    'Arıza Konumu Failure Location': 'failure_location',
    'Arıza Tespit Yöntemi Failure Detection Method': 'detection_method',
    'Kapsam Scope': 'scope',
    'İlgili Tedarikçi Relevant Supplier': 'supplier',
    'Proje Bazında Fracas ID Fracas ID Based on Project': 'project_fracas_id',
    'Arıza Tanımı Failure Description': 'failure_description',
    'DDU Arıza Sınıfı DDU Failure Class': 'ddu_failure_class',
    'Arıza Sınıfı Failure Class': 'failure_class',
    'Arızanın Emniyetle İlgili Şiddet Kategorisi Safety Related Severity Category of Failure': 'safety_severity',
    'Arıza Kaynağı Source of Failure': 'failure_source',
    'Arıza Tespitini Takiben Yapılan İşlem Action Followed by Fault Detection': 'action_after_detection',
    'Aksiyon Action': 'action',
    'Garanti Kapsamı Warranty Coverage': 'warranty_coverage',
    'Tamir için Gerekli Personel Sayısı Required Personnel Quantity for Repair': 'personnel_count',
    'Tamir/Değiştirme Başlama Tarihi Date of Starting to Repair/Replace': 'repair_start_date',
    'Tamir/Değiştirme Başlama Saati Time of Starting to Repair/Replace': 'repair_start_time',
    'Tamir/Değiştirme Bitiş Tarihi Date of Fnish to Repair/Replace': 'repair_end_date',
    'Tamir/Değiştirme Bitiş Saati Time of Fnish to Repair/Replace': 'repair_end_time',
    'Tamir Süresi (dakika) Repair Time (dakika)': 'repair_time_minutes',
    'Tamir Süresi (saat) Repair Time (hour)': 'repair_time_hours',
    'Servise Veriliş Tarih Date of Ready to Service': 'service_ready_date',
    'Servise Veriliş Saati Time of Ready to Service': 'service_ready_time',
    'Arıza Tipi Failure Type': 'failure_type',
    'Detaylı Bilgi Detail İnformation': 'detail_info',
    'NCR Numarası NCR Number': 'ncr_number',
    'NCR Kapanış Tarihi NCR Closing Date': 'ncr_closing_date',
    'Araç MTTR / MDT': 'vehicle_mttr',
    'Kompanent MTTR / MDT': 'component_mttr',
    'Ekipman Tedarikçisi Equipment Supplier': 'equipment_supplier',
    'Parça Kodu Part Code': 'part_code',
    'Seri Numarası Serial Number': 'serial_number',
    'Parça Adı Part Name': 'part_name',
    'Adet Quantity': 'quantity',
    'Sipariş No Order No': 'order_no',
    'Sipariş Tarihi Order Date': 'order_date',
    'Teslim Tarihi Delivery Date': 'delivery_date',
    'Malzeme Maliyeti Material Cost': 'material_cost',
    'İşçilik Maliyeti Labor Cost': 'labor_cost',
    'Photo URL': 'photo_url',
    'Arıza Resmi': 'failure_image',
    'Arıza Kaynağı (Sorumlu )': 'responsible_source',
    'Arıza Kaynağı (Sorumlu 2)': 'responsible_source_2',
    'Bekleme süresi (dk)': 'waiting_time_minutes',
    'Tamir süresi (dk)': 'repair_duration_minutes',
    'Toplam Arıza süresi (dk)': 'total_failure_time_minutes',
    'Bekleme gecikme oranı': 'waiting_delay_ratio',
    'bekleme süresi': 'waiting_time',
    'tamir süresi': 'repair_duration',
    'arızalı kalma süresi': 'downtime',
    'toplam arıza süresi': 'total_downtime'
}


def get_excel_path(project_code=None):
    """Projenin FRACAS Excel dosya yolunu döndür"""
    if not project_code:
        project_code = session.get('current_project', 'belgrad')
    
    return ProjectManager.get_fracas_file(project_code)


def load_fracas_data(project_code=None):
    """Projenin FRACAS verilerini yükle"""
    if not project_code:
        project_code = session.get('current_project', 'belgrad')
    
    excel_path = ProjectManager.get_fracas_file(project_code)
    
    if not excel_path or not os.path.exists(excel_path):
        return None
    
    try:
        # Path'e göre header satırını belirle
        if 'logs' in excel_path and 'ariza_listesi' in excel_path:
            # logs/{project}/ariza_listesi/Fracas_*.xlsx format (header 4. satırda)
            df = pd.read_excel(excel_path, sheet_name='FRACAS', header=3)
        else:
            # Fallback: data/ klasöründen (header 1. satırda)
            df = pd.read_excel(excel_path, sheet_name='FRACAS', header=0)
        
        # Sütun isimlerini normalize et
        df.columns = df.columns.str.replace('\n', ' ', regex=False).str.replace('\r', '', regex=False)
        df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
        
        # FRACAS ID kolonunu bul ve boş satırları filtrele
        fracas_col = None
        for col in df.columns:
            if 'fracas' in col.lower() and 'id' in col.lower():
                fracas_col = col
                break
        if fracas_col:
            df = df[df[fracas_col].notna()]
        
        return df
    except Exception as e:
        logger.error(f'Excel okuma hatasi ({project_code}): {e}')
        return None


def load_ariza_listesi_data():
    """Arıza Listesi Excel'den verileri yükle - logs/{project}/ariza_listesi/'den"""
    current_project = session.get('current_project', 'belgrad')
    
    # Birincil konum: logs/{project}/ariza_listesi/Ariza_Listesi_{PROJECT}.xlsx
    ariza_dir = os.path.join(current_app.root_path, 'logs', current_project, 'ariza_listesi')
    ariza_listesi_file = None
    
    # logs/{project}/ariza_listesi/ klasöründen ara
    if os.path.exists(ariza_dir):
        for file in os.listdir(ariza_dir):
            if file.endswith('.xlsx') and not file.startswith('~$'):
                ariza_listesi_file = os.path.join(ariza_dir, file)
                use_sheet = 'Ariza Listesi'  # Arıza Listesi sayfası
                header_row = 3  # header 4. satırda (0-indexed)
                break
    
    # Fallback: data/{project}/Veriler.xlsx
    if not ariza_listesi_file:
        veriler_file = os.path.join(current_app.root_path, 'data', current_project, 'Veriler.xlsx')
        if os.path.exists(veriler_file):
            ariza_listesi_file = veriler_file
            use_sheet = 'Veriler'  # Veriler.xlsx sayfası
            header_row = 0  # header ilk satırda
    
    if not ariza_listesi_file:
        return None
    
    try:
        # Sheet seçimi yapılmadıysa default'ı dene
        sheet_name = use_sheet if 'use_sheet' in locals() else 'Veriler'
        header = header_row if 'header_row' in locals() else 0
        
        df = pd.read_excel(ariza_listesi_file, sheet_name=sheet_name, header=header)
        # Sütun isimlerini normalize et
        df.columns = df.columns.str.replace('\n', ' ', regex=False).str.replace('\r', '', regex=False)
        df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
        
        # FRACAS ID kolonunu bul ve boş satırları filtrele (varsa)
        fracas_col = None
        for col in df.columns:
            if 'fracas' in col.lower() and 'id' in col.lower():
                fracas_col = col
                break
        if fracas_col:
            df = df[df[fracas_col].notna()]
        
        # Sadece doldurulmuş satırları al
        if len(df) > 0:
            return df
        
        return None
    except Exception as e:
        logger.error(f'Ariza Listesi okuma hatasi: {e}')
        return None


def safe_numeric(value, default=0):
    """Güvenli sayısal dönüşüm"""
    try:
        if pd.isna(value):
            return default
        return float(value)
    except:
        return default


@bp.route('/')
@login_required
def index():
    """FRACAS Ana Sayfa - Özet Dashboard - Arıza Listesi verileri kullanarak"""
    # Tüm kullanıcılara açık
    
    # URL'deki ?project parametresini veya sessiyon'daki current_project'i kullan
    project_code = request.args.get('project') or session.get('current_project', 'belgrad')
    
    # DEBUG
    logger.info(f'[FRACAS DEBUG] request.args.project={request.args.get("project")}')
    logger.info(f'[FRACAS DEBUG] session.current_project={session.get("current_project")}')
    logger.info(f'[FRACAS DEBUG] final project_code={project_code}')
    
    # Session'a kaydet (sonraki isteklerde de kullanılabilsin)
    if project_code:
        session['current_project'] = project_code
        session.modified = True
    
    try:
        # Veri yükle
        logger.info(f'[FRACAS] Veri yükleniyor... (project: {project_code})')
        df = load_fracas_data(project_code)
        logger.info(f'[FRACAS] Veri yüklendi: {len(df) if df is not None else 0} satır')
        
        project_name = project_code.upper() if project_code else 'BILINMEYEN'
        data_source = f'Fracas_{project_name}' if df is not None and len(df) > 0 else 'Veri Yok'
        
        if df is None:
            flash(f'{project_code.upper()} için FRACAS verileri bulunamadı. Dosya: logs/{project_code}/ariza_listesi/Fracas_{project_code.upper()}.xlsx', 'warning')
            return render_template('fracas/index.html', data_available=False, data_source=f'Veri Yok ({project_code})')
        
        # Temel istatistikler - cache ile
        cache_key = f"fracas:{project_code}:analysis"
        cached_analysis = None
        try:
            from app import cache_manager
            cached_analysis = cache_manager.get(cache_key)
        except Exception:
            pass
        
        if cached_analysis:
            stats = cached_analysis['stats']
            rams_metrics = cached_analysis['rams_metrics']
            pareto_data = cached_analysis['pareto_data']
            trend_data = cached_analysis['trend_data']
            supplier_data = cached_analysis['supplier_data']
            cost_data = cached_analysis['cost_data']
            logger.info('[FRACAS] Cache hit - veriler cache\'den yüklendi')
        else:
            logger.info('[FRACAS] basic_stats hesaplanıyor...')
            stats = calculate_basic_stats(df)
            logger.info('[FRACAS] basic_stats OK')
            
            logger.info('[FRACAS] rams_metrics hesaplanıyor...')
            rams_metrics = calculate_rams_metrics(df)
            logger.info('[FRACAS] rams_metrics OK')
            
            logger.info('[FRACAS] pareto_analysis hesaplanıyor...')
            pareto_data = calculate_pareto_analysis(df)
            logger.info('[FRACAS] pareto_analysis OK')
            
            logger.info('[FRACAS] trend_analysis hesaplanıyor...')
            trend_data = calculate_trend_analysis(df)
            logger.info('[FRACAS] trend_analysis OK')
            
            logger.info('[FRACAS] supplier_analysis hesaplanıyor...')
            supplier_data = calculate_supplier_analysis(df)
            logger.info('[FRACAS] supplier_analysis OK')
            
            logger.info('[FRACAS] cost_analysis hesaplanıyor...')
            cost_data = calculate_cost_analysis(df)
            logger.info('[FRACAS] cost_analysis OK')
            
            # Cache'e kaydet (1 saat TTL)
            try:
                from app import cache_manager
                cache_manager.set(cache_key, {
                    'stats': stats,
                    'rams_metrics': rams_metrics,
                    'pareto_data': pareto_data,
                    'trend_data': trend_data,
                    'supplier_data': supplier_data,
                    'cost_data': cost_data
                }, CacheConfig.TTL_MEDIUM)
                logger.info('[FRACAS] Veriler cache\'e kaydedildi')
            except Exception:
                pass
        
        # Veri kalitesi analizi (cache dışında, hafif hesaplama)
        data_quality = calculate_data_quality(df)
        
        logger.info('[FRACAS] Template render ediliyor...')
        
        logger.info('[FRACAS] Template için verileri hazırlanıyor...')
        
        # Template için verileri hazırla - list comprehension kesmeyin template'de
        pareto_labels_module = [item['name'][:20] for item in pareto_data['by_module']]
        pareto_counts_module = [item['count'] for item in pareto_data['by_module']]
        pareto_cumulative_module = [item['cumulative'] for item in pareto_data['by_module']]
        logger.info(f'[FRACAS] pareto_module: {len(pareto_labels_module)} items')
        
        pareto_labels_supplier = [item['name'][:20] for item in pareto_data['by_supplier']]
        pareto_counts_supplier = [item['count'] for item in pareto_data['by_supplier']]
        pareto_cumulative_supplier = [item['cumulative'] for item in pareto_data['by_supplier']]
        logger.info(f'[FRACAS] pareto_supplier: {len(pareto_labels_supplier)} items')
        
        pareto_labels_location = [item['name'][:25] for item in pareto_data['by_location']]
        pareto_counts_location = [item['count'] for item in pareto_data['by_location']]
        pareto_cumulative_location = [item['cumulative'] for item in pareto_data['by_location']]
        logger.info(f'[FRACAS] pareto_location: {len(pareto_labels_location)} items')
        
        pareto_labels_class = [item['name'][:30] for item in pareto_data['by_failure_class']]
        pareto_counts_class = [item['count'] for item in pareto_data['by_failure_class']]
        pareto_cumulative_class = [item['cumulative'] for item in pareto_data['by_failure_class']]
        logger.info(f'[FRACAS] pareto_class: {len(pareto_labels_class)} items')
        
        trend_periods = [item['period'] for item in trend_data['monthly']]
        trend_counts = [item['count'] for item in trend_data['monthly']]
        logger.info(f'[FRACAS] trend_periods: {len(trend_periods)} items')
        
        trend_hours = [item['hour'] for item in trend_data['by_hour']]
        trend_hour_counts = [item['count'] for item in trend_data['by_hour']]
        logger.info(f'[FRACAS] trend_hours: {len(trend_hours)} items')
        
        trend_days = [item['day'] for item in trend_data['by_weekday']]
        trend_day_counts = [item['count'] for item in trend_data['by_weekday']]
        logger.info(f'[FRACAS] trend_days: {len(trend_days)} items')
        
        return render_template('fracas/index.html',
                             data_available=True,
                             data_source=data_source,
                             stats=stats,
                             rams=rams_metrics,
                             pareto=pareto_data,
                             pareto_labels_module=pareto_labels_module,
                             pareto_counts_module=pareto_counts_module,
                             pareto_cumulative_module=pareto_cumulative_module,
                             pareto_labels_supplier=pareto_labels_supplier,
                             pareto_counts_supplier=pareto_counts_supplier,
                             pareto_cumulative_supplier=pareto_cumulative_supplier,
                             pareto_labels_location=pareto_labels_location,
                             pareto_counts_location=pareto_counts_location,
                             pareto_cumulative_location=pareto_cumulative_location,
                             pareto_labels_class=pareto_labels_class,
                             pareto_counts_class=pareto_counts_class,
                             pareto_cumulative_class=pareto_cumulative_class,
                             trend_periods=trend_periods,
                             trend_counts=trend_counts,
                             trend_hours=trend_hours,
                             trend_hour_counts=trend_hour_counts,
                             trend_days=trend_days,
                             trend_day_counts=trend_day_counts,
                             trend=trend_data,
                             supplier=supplier_data,
                             cost=cost_data,
                             data_quality=data_quality,
                             total_records=len(df))
    except Exception as e:
        logger.error(f'[FRACAS] HATA: {e}', exc_info=True)
        flash(f'FRACAS verileri yüklenirken hata: {str(e)}', 'danger')
        return render_template('fracas/index.html', data_available=False, data_source='Hata')


def get_column(df, possible_names):
    """Olası kolon isimlerinden birini bul - tam, kısmi ve fuzzy eşleştirme"""
    from difflib import SequenceMatcher
    
    # 1. Tam eşleştirme
    for col in df.columns:
        col_clean = col.strip().lower()
        for name in possible_names:
            if name.lower() == col_clean:
                return col
    
    # 2. Kısmi eşleştirme (içerme kontrolü)
    for col in df.columns:
        col_lower = col.lower()
        for name in possible_names:
            if name.lower() in col_lower or col_lower in name.lower():
                return col
    
    # 3. Fuzzy eşleştirme (benzerlik oranı >= 0.7)
    best_match = None
    best_ratio = 0.0
    for col in df.columns:
        col_lower = col.strip().lower()
        for name in possible_names:
            ratio = SequenceMatcher(None, name.lower(), col_lower).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = col
    
    if best_ratio >= 0.7:
        return best_match
    
    return None


def calculate_data_quality(df):
    """Veri kalitesi kontrolü - kritik kolonlardaki doluluk oranını hesapla"""
    if df is None or df.empty:
        return {'score': 0, 'details': [], 'total_rows': 0}
    
    # Kritik kolonlar ve beklenen isimleri
    critical_columns = [
        ('Araç No', ['araç', 'araç no', 'araç numarası', 'tram', 'vehicle']),
        ('Tarih', ['tarih', 'date', 'hata tarih', 'arıza tarihi']),
        ('Modül/Sistem', ['modül', 'sistem', 'module', 'system']),
        ('Arıza Sınıfı', ['arıza sınıfı', 'failure class', 'sınıf']),
        ('Tamir Süresi', ['tamir süresi', 'repair time']),
        ('Tedarikçi', ['tedarikçi', 'supplier']),
        ('KM', ['km', 'muhasebe km', 'kilometre', 'araç kilometresi']),
    ]
    
    total_rows = len(df)
    details = []
    filled_scores = []
    
    for label, possible_names in critical_columns:
        col = get_column(df, possible_names)
        if col:
            non_null = df[col].dropna().count()
            fill_rate = round((non_null / total_rows) * 100, 1) if total_rows > 0 else 0
            details.append({'column': label, 'fill_rate': fill_rate, 'found': True})
            filled_scores.append(fill_rate)
        else:
            details.append({'column': label, 'fill_rate': 0, 'found': False})
            filled_scores.append(0)
    
    overall_score = round(sum(filled_scores) / len(filled_scores), 1) if filled_scores else 0
    
    return {
        'score': overall_score,
        'details': details,
        'total_rows': total_rows
    }


def calculate_basic_stats(df):
    """Temel istatistikleri hesapla - Arıza Listesi verileriyle"""
    # Kolon isimlerini dinamik bul
    vehicle_col = get_column(df, ['araç', 'araç no', 'tram', 'vehicle'])
    module_col = get_column(df, ['modül', 'sistem', 'module', 'system'])
    supplier_col = get_column(df, ['tedarikçi', 'supplier', 'supplier name'])
    class_col = get_column(df, ['arıza sınıfı', 'failure class', 'sınıf'])
    date_col = get_column(df, ['tarih', 'date', 'hata tarih'])
    warranty_col = get_column(df, ['garanti', 'warranty'])
    
    stats = {
        'total_failures': len(df),
        'unique_vehicles': df[vehicle_col].nunique() if vehicle_col else 0,
        'unique_modules': df[module_col].nunique() if module_col else 0,
        'total_suppliers': df[supplier_col].nunique() if supplier_col else 0,
        'class_a': 0,
        'class_b': 0,
        'class_c': 0,
        'class_d': 0,
        'warranty_claims': 0
    }
    
    # Arıza sınıfı dağılımı
    if class_col:
        for sinif in df[class_col].dropna():
            sinif_str = str(sinif).strip()
            if sinif_str.startswith('A'):
                stats['class_a'] += 1
            elif sinif_str.startswith('B'):
                stats['class_b'] += 1
            elif sinif_str.startswith('C'):
                stats['class_c'] += 1
            elif sinif_str.startswith('D'):
                stats['class_d'] += 1
    
    # Garanti kapsamı
    if warranty_col:
        warranty_data = df[warranty_col].astype(str).str.lower()
        stats['warranty_claims'] = int(warranty_data.str.contains('evet|yes|garanti|warranty', na=False).sum())
    
    return stats


def calculate_rams_metrics(df):
    """EN 50126 RAMS metriklerini hesapla - Arıza Listesi verilerine göre"""
    rams = {
        'mtbf': None,
        'mtbf_time': None,
        'mttr': None,
        'mdt': None,
        'mwt': None,
        'availability': None,
        'reliability': None
    }
    
    if len(df) == 0:
        return rams
    
    # MTTR hesaplama - Tamir Süresi (dakika veya saat)
    mttr_col = get_column(df, ['tamir süresi (dakika)', 'tamir süresi (saat)', 'tamir süresi', 'repair time'])
    if mttr_col:
        valid_data = pd.to_numeric(df[mttr_col], errors='coerce').dropna()
        if len(valid_data) > 0:
            # Eğer sütun "saat" ise dakikaya çevir
            if 'saat' in str(mttr_col).lower():
                rams['mttr'] = float(round(valid_data.mean() * 60, 2))  # Saat -> dakika
            else:
                rams['mttr'] = float(round(valid_data.mean(), 2))  # Zaten dakika
    
    # Bekleme süresi
    wait_col = get_column(df, ['bekleme süresi', 'waiting time', 'waiting'])
    if wait_col:
        valid_data = pd.to_numeric(df[wait_col], errors='coerce').dropna()
        if len(valid_data) > 0:
            rams['mwt'] = float(round(valid_data.mean(), 2))
    
    # MDT = MTTR + MWT
    if rams['mttr'] is not None and rams['mwt'] is not None:
        rams['mdt'] = float(round(rams['mttr'] + rams['mwt'], 2))
    elif rams['mttr'] is not None:
        rams['mdt'] = rams['mttr']
    
    # MTBF hesaplama
    # Arıza Listesi'ndeki araçların çalışma süresi bilgisi varsa kullan
    km_col = get_column(df, ['km', 'muhasebe km', 'kilometre'])
    
    if km_col:
        # KM verilerinden MTBF hesapla: Araç başına ortalama KM / Araç başına ortalama arıza sayısı
        vehicle_col = get_column(df, ['araç', 'araç no', 'tram', 'vehicle'])
        if vehicle_col:
            vehicle_km = df.groupby(vehicle_col)[km_col].apply(lambda x: pd.to_numeric(x, errors='coerce').max() - pd.to_numeric(x, errors='coerce').min())
            avg_km_per_vehicle = vehicle_km[vehicle_km > 0].mean() if len(vehicle_km[vehicle_km > 0]) > 0 else 50000
            
            total_vehicles = df[vehicle_col].nunique()
            failures_per_vehicle = len(df) / total_vehicles if total_vehicles > 0 else 1
            
            # MTBF = Ortalama araç KM / Arıza sayısı
            mtbf_km = avg_km_per_vehicle / failures_per_vehicle if failures_per_vehicle > 0 else avg_km_per_vehicle
            # KM'i saate çevir (100 km/saat varsayımı)
            rams['mtbf'] = float(round((mtbf_km / 100) * 60, 2))  # dakika
    else:
        # KM verisi yoksa, aylık çalışma saati tahmini kullan (daha gerçekçi: 480 saat/ay)
        vehicle_col = get_column(df, ['araç', 'araç no', 'tram', 'vehicle'])
        total_vehicles = df[vehicle_col].nunique() if vehicle_col else 1
        failures_per_vehicle = len(df) / total_vehicles if total_vehicles > 0 else 1
        mtbf_hours = 480 / failures_per_vehicle if failures_per_vehicle > 0 else 480
        rams['mtbf'] = float(round(mtbf_hours * 60, 2))  # Dakikaya çevir
    
    # Zaman bazlı MTBF hesaplama (tarih aralığından)
    date_col = get_column(df, ['tarih', 'date', 'hata tarih', 'arıza tarihi'])
    if date_col:
        try:
            dates = pd.to_datetime(df[date_col], errors='coerce').dropna()
            if len(dates) >= 2:
                date_range_days = (dates.max() - dates.min()).days
                if date_range_days > 0:
                    vehicle_col_t = get_column(df, ['araç', 'araç no', 'tram', 'vehicle'])
                    total_vehicles_t = df[vehicle_col_t].nunique() if vehicle_col_t else 1
                    total_vehicles_t = max(total_vehicles_t, 1)
                    # Araç başına operasyon süresi (gün) * 16 saat/gün * 60 dk/saat / araç başına arıza sayısı
                    total_op_minutes = date_range_days * 16 * 60 * total_vehicles_t
                    mtbf_time = total_op_minutes / len(df)
                    rams['mtbf_time'] = float(round(mtbf_time, 2))
        except Exception as e:
            logger.warning(f'Zaman bazlı MTBF hesaplama hatası: {e}')
    
    # Kullanılabilirlik = MTBF / (MTBF + MTTR)
    if rams['mtbf'] and rams['mttr']:
        availability = (rams['mtbf'] / (rams['mtbf'] + rams['mttr'])) * 100
        rams['availability'] = float(round(max(0, min(100, availability)), 2))
    
    # Reliability (İtfaiye oranı) - Başarılı onarım yüzdesi
    # Arıza Listesi'nde "Onarım Veya Onarım Dışı" veya benzeri sütun varsa kullan
    repair_col = get_column(df, ['onarım', 'repair', 'onarım veya onarım dışı', 'status'])
    if repair_col:
        successful_repairs = df[repair_col].astype(str).str.lower().str.contains('onarım|repair|fixed|başarılı', na=False).sum()
        rams['reliability'] = float(round((successful_repairs / len(df)) * 100, 1)) if len(df) > 0 else None
    else:
        rams['reliability'] = None  # Veri yoksa N/A göster
    
    return rams


def calculate_pareto_analysis(df):
    """Pareto analizi - En çok arıza veren modül/tedarikçi"""
    logger.info(f'[PARETO] DataFrame columns: {list(df.columns)[:10]}...')  # İlk 10 kolonu göster
    
    pareto = {
        'by_module': [],
        'by_supplier': [],
        'by_location': [],
        'by_failure_class': []
    }
    
    # Modül bazlı (Araç Modül sütununu kullan)
    module_col = get_column(df, ['araç module', 'vehicle module', 'modül'])
    logger.info(f'[PARETO] module_col bulundu: {module_col}')
    if module_col:
        module_counts = df[module_col].value_counts().head(10)
        total = module_counts.sum()
        cumulative = 0
        for module, count in module_counts.items():
            cumulative += count
            # Sanitize the name: remove newlines and extra spaces
            name_str = str(module).replace('\n', ' ').replace('\r', '').strip()
            pareto['by_module'].append({
                'name': name_str,
                'count': int(count),
                'percentage': float(round(count / total * 100, 1)),
                'cumulative': float(round(cumulative / total * 100, 1))
            })
    
    # Tedarikçi bazlı
    supplier_col = get_column(df, ['tedarikçi', 'supplier', 'relevant supplier'])
    logger.info(f'[PARETO] supplier_col bulundu: {supplier_col}')
    if supplier_col:
        supplier_counts = df[supplier_col].value_counts().head(10)
        total = supplier_counts.sum()
        cumulative = 0
        for supplier, count in supplier_counts.items():
            cumulative += count
            # Sanitize the name
            name_str = str(supplier).replace('\n', ' ').replace('\r', '').strip()
            pareto['by_supplier'].append({
                'name': name_str,
                'count': int(count),
                'percentage': float(round(count / total * 100, 1)),
                'cumulative': float(round(cumulative / total * 100, 1))
            })
    
    # Konum bazlı (Alt Sistem sütununu kullan)
    location_col = get_column(df, ['sistem', 'alt sistem', 'failure location', 'location'])
    logger.info(f'[PARETO] location_col bulundu: {location_col}')
    if location_col:
        location_counts = df[location_col].value_counts().head(10)
        total = location_counts.sum()
        cumulative = 0
        for location, count in location_counts.items():
            cumulative += count
            # Sanitize the name
            name_str = str(location).replace('\n', ' ').replace('\r', '').strip()
            pareto['by_location'].append({
                'name': name_str,
                'count': int(count),
                'percentage': float(round(count / total * 100, 1)),
                'cumulative': float(round(cumulative / total * 100, 1))
            })
    
    # Arıza sınıfı bazlı
    class_col = get_column(df, ['arıza sınıfı', 'failure class', 'sınıf', 'failure'])
    logger.info(f'[PARETO] class_col bulundu: {class_col}')
    if class_col:
        class_counts = df[class_col].value_counts().head(10)
        total = class_counts.sum()
        cumulative = 0
        for cls, count in class_counts.items():
            cumulative += count
            # Sanitize the name
            name_str = str(cls).replace('\n', ' ').replace('\r', '').strip()
            pareto['by_failure_class'].append({
                'name': name_str,
                'count': int(count),
                'percentage': float(round(count / total * 100, 1)),
                'cumulative': float(round(cumulative / total * 100, 1))
            })
    
    return pareto


def calculate_trend_analysis(df):
    """Zaman bazlı trend analizi"""
    trend = {
        'monthly': [],
        'by_hour': [],
        'by_weekday': []
    }
    
    # Tarih sütununu bul
    date_col = get_column(df, ['tarih', 'date', 'hata tarih', 'arıza tarihi'])
    
    if date_col:
        try:
            # Tarih sütununu parse et - Datetime nesnelerine dönüştür
            df['parsed_date'] = pd.to_datetime(df[date_col], errors='coerce', utc=False)
            valid_dates = df[df['parsed_date'].notna()].copy()
            
            if len(valid_dates) > 0:
                # Aylık trend
                monthly = valid_dates.groupby(valid_dates['parsed_date'].dt.to_period('M')).size()
                for period, count in monthly.tail(12).items():
                    trend['monthly'].append({
                        'period': str(period),
                        'count': int(count)
                    })
                
                # Saat bazlı analiz
                hourly = valid_dates.groupby(valid_dates['parsed_date'].dt.hour).size()
                for hour in range(24):
                    count = hourly.get(hour, 0)
                    trend['by_hour'].append({
                        'hour': f'{hour:02d}:00',
                        'count': int(count)
                    })
                
                # Haftanın günü bazlı analiz
                weekday_map = {0: 'Pazartesi', 1: 'Salı', 2: 'Çarşamba', 3: 'Perşembe', 4: 'Cuma', 5: 'Cumartesi', 6: 'Pazar'}
                weekday = valid_dates.groupby(valid_dates['parsed_date'].dt.dayofweek).size()
                for day_num in range(7):
                    count = weekday.get(day_num, 0)
                    trend['by_weekday'].append({
                        'day': weekday_map[day_num],
                        'count': int(count)
                    })
        except Exception as e:
            logger.error(f'Tarih analizi hatasi: {e}')
            import traceback
            traceback.print_exc()
    
    return trend


def calculate_supplier_analysis(df):
    """Tedarikçi performans analizi"""
    supplier_data = {
        'performance': [],
        'mttr_by_supplier': []
    }
    
    supplier_col = get_column(df, ['tedarikçi', 'supplier'])
    if not supplier_col:
        return supplier_data
    
    # Tedarikçi bazlı arıza sayısı ve MTTR
    repair_col = get_column(df, ['tamir süresi', 'mttr (dk)', 'tamir süresi (dakika)', 'repair time'])
    
    suppliers = df[supplier_col].dropna().unique()
    
    for supplier in suppliers[:15]:  # İlk 15 tedarikçi
        supplier_df = df[df[supplier_col] == supplier]
        
        # Sanitize supplier name
        supplier_name = str(supplier).replace('\n', ' ').replace('\r', '').strip()
        
        perf = {
            'name': supplier_name,
            'failure_count': len(supplier_df),
            'avg_repair_time': None
        }
        
        if repair_col:
            valid_repair = pd.to_numeric(supplier_df[repair_col], errors='coerce').dropna()
            if len(valid_repair) > 0:
                perf['avg_repair_time'] = float(round(valid_repair.mean(), 1))
        
        supplier_data['performance'].append(perf)
    
    # En yüksek arıza sayısına göre sırala
    supplier_data['performance'].sort(key=lambda x: x['failure_count'], reverse=True)
    
    return supplier_data


def calculate_cost_analysis(df):
    """Maliyet analizi"""
    cost_data = {
        'total_material': 0,
        'total_labor': 0,
        'total_cost': 0,
        'by_vehicle': [],
        'by_supplier': [],
        'warranty_cost': 0,
        'non_warranty_cost': 0
    }
    
    # Malzeme ve işçilik maliyeti - Arıza Listesi'nde olmayabilir
    material_col = get_column(df, ['malzeme maliyeti', 'material cost'])
    labor_col = get_column(df, ['işçilik maliyeti', 'labor cost'])
    
    if material_col:
        cost_data['total_material'] = float(round(pd.to_numeric(df[material_col], errors='coerce').sum(), 2))
    
    if labor_col:
        cost_data['total_labor'] = float(round(pd.to_numeric(df[labor_col], errors='coerce').sum(), 2))
    
    cost_data['total_cost'] = cost_data['total_material'] + cost_data['total_labor']
    
    # Garanti kapsamı
    warranty_col = get_column(df, ['garanti kapsamı', 'garanti', 'warranty'])
    if warranty_col:
        warranty_data = df[warranty_col].astype(str).str.lower()
        warranty_count = int(warranty_data.str.contains('evet|yes|garanti|warranty|covered', na=False).sum())
        cost_data['warranty_cost'] = warranty_count
        cost_data['non_warranty_cost'] = len(df) - warranty_count
    
    return cost_data


@bp.route('/api/summary')
@login_required
def api_summary():
    """API: Özet veriler"""
    df = load_fracas_data()
    if df is None:
        return jsonify({'error': 'Veri bulunamadı'}), 404
    
    return jsonify({
        'stats': calculate_basic_stats(df),
        'rams': calculate_rams_metrics(df)
    })


@bp.route('/api/pareto/<string:category>')
@login_required
def api_pareto(category):
    """API: Pareto analizi"""
    df = load_ariza_listesi_data()
    if df is None:
        return jsonify({'error': 'Veri bulunamadı'}), 404
    
    pareto = calculate_pareto_analysis(df)
    
    if pareto is None or category not in pareto:
        return jsonify({'error': 'Geçersiz kategori'}), 400
    
    return jsonify(pareto[category])


@bp.route('/api/trend')
@login_required
def api_trend():
    """API: Trend analizi"""
    df = load_ariza_listesi_data()
    if df is None:
        df = load_fracas_data()
    if df is None:
        return jsonify({'error': 'Veri bulunamadı'}), 404
    
    return jsonify(calculate_trend_analysis(df))


@bp.route('/api/supplier')
@login_required
def api_supplier():
    """API: Tedarikçi analizi"""
    df = load_fracas_data()
    if df is None:
        return jsonify({'error': 'Veri bulunamadı'}), 404
    
    return jsonify(calculate_supplier_analysis(df))


@bp.route('/api/cost')
@login_required
def api_cost():
    """API: Maliyet analizi"""
    df = load_fracas_data()
    if df is None:
        return jsonify({'error': 'Veri bulunamadı'}), 404
    
    return jsonify(calculate_cost_analysis(df))


@bp.route('/api/vehicle/<string:vehicle_id>')
@login_required
def api_vehicle_detail(vehicle_id):
    """API: Araç detay analizi"""
    df = load_ariza_listesi_data()
    if df is None:
        return jsonify({'error': 'Veri bulunamadı'}), 404
    
    # Araç sütununu bul
    vehicle_col = get_column(df, ['araç', 'araç no', 'tram', 'vehicle'])
    if not vehicle_col:
        return jsonify({'error': 'Araç sütunu bulunamadı'}), 400
    
    vehicle_df = df[df[vehicle_col].astype(str) == str(vehicle_id)]
    
    if len(vehicle_df) == 0:
        return jsonify({'error': 'Araç bulunamadı'}), 404
    
    # Modül ve arıza sınıfı sütunlarını bul
    module_col = get_column(vehicle_df, ['modül', 'sistem', 'module', 'system'])
    class_col = get_column(vehicle_df, ['arıza sınıfı', 'failure class'])
    
    result = {
        'vehicle_id': vehicle_id,
        'total_failures': len(vehicle_df),
        'modules': {},
        'failure_classes': {}
    }
    
    if module_col:
        result['modules'] = vehicle_df[module_col].value_counts().to_dict()
    if class_col:
        result['failure_classes'] = vehicle_df[class_col].value_counts().to_dict()
    
    return jsonify(result)


@bp.route('/api/km-analysis')
@login_required
def api_km_analysis():
    """API: Kilometre bazlı arıza analizi"""
    df = load_fracas_data()
    if df is None:
        return jsonify({'error': 'Veri bulunamadı'}), 404
    
    # KM sütununu bul
    km_col = get_column(df, ['km', 'muhasebe km', 'kilometre'])
    if not km_col:
        return jsonify({'error': 'Kilometre sütunu bulunamadı'}), 400
    
    df['km'] = pd.to_numeric(df[km_col], errors='coerce')
    valid_km = df[df['km'].notna()]
    
    if len(valid_km) == 0:
        return jsonify({'error': 'Geçerli kilometre verisi bulunamadı'}), 400
    
    # Kilometre aralıkları
    bins = [0, 10000, 25000, 50000, 75000, 100000, 150000, 200000, float('inf')]
    labels = ['0-10K', '10K-25K', '25K-50K', '50K-75K', '75K-100K', '100K-150K', '150K-200K', '200K+']
    
    valid_km['km_range'] = pd.cut(valid_km['km'], bins=bins, labels=labels)
    km_counts = valid_km['km_range'].value_counts().sort_index()
    
    result = []
    for label in labels:
        result.append({
            'range': label,
            'count': int(km_counts.get(label, 0))
        })
    
    return jsonify(result)


@bp.route('/filter', methods=['GET'])
@login_required
def fracas_filter():
    """FRACAS verileri filtrele - Tarih ve kategori"""
    df = load_fracas_data()
    
    if df is None:
        return jsonify({'error': 'Veri bulunamadı'}), 404
    
    # Filtre parametreleri
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    failure_class = request.args.get('failure_class')
    supplier = request.args.get('supplier')
    
    # Tarih sütununu bul
    date_col = get_column(df, ['tarih', 'date', 'hata tarih', 'failure date'])
    
    # Filtreleri uygula
    filtered_df = df.copy()
    
    # Tarih filtresi
    if start_date and date_col:
        try:
            start = pd.to_datetime(start_date)
            filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], errors='coerce')
            filtered_df = filtered_df[filtered_df[date_col] >= start]
        except:
            pass
    
    if end_date and date_col:
        try:
            end = pd.to_datetime(end_date)
            filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], errors='coerce')
            filtered_df = filtered_df[filtered_df[date_col] <= end]
        except:
            pass
    
    # Arıza sınıfı filtresi
    if failure_class:
        class_col = get_column(filtered_df, ['arıza sınıfı', 'failure class', 'sınıf'])
        if class_col:
            filtered_df = filtered_df[filtered_df[class_col].astype(str).str.startswith(failure_class)]
    
    # Tedarikçi filtresi
    if supplier:
        supplier_col = get_column(filtered_df, ['tedarikçi', 'supplier', 'supplier name'])
        if supplier_col:
            filtered_df = filtered_df[filtered_df[supplier_col].astype(str).str.contains(supplier, case=False, na=False)]
    
    # İstatistikler
    stats = calculate_basic_stats(filtered_df)
    pareto = calculate_pareto_analysis(filtered_df)
    trend = calculate_trend_analysis(filtered_df)
    
    return jsonify({
        'success': True,
        'total_records': len(filtered_df),
        'filtered_count': len(filtered_df),
        'stats': stats,
        'pareto': pareto,
        'trend': trend
    })


@bp.route('/export/excel', methods=['GET'])
@login_required
def export_excel():
    """FRACAS verileri Excel'e aktar"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from io import BytesIO
    
    df = load_fracas_data()
    
    if df is None:
        flash('FRACAS verileri bulunamadı!', 'danger')
        return redirect(url_for('fracas.index'))
    
    # Filtre parametreleri
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    failure_class = request.args.get('failure_class')
    
    date_col = get_column(df, ['tarih', 'date', 'hata tarih'])
    filtered_df = df.copy()
    
    # Filtreler uygula
    if start_date and date_col:
        try:
            start = pd.to_datetime(start_date)
            filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], errors='coerce')
            filtered_df = filtered_df[filtered_df[date_col] >= start]
        except:
            pass
    
    if end_date and date_col:
        try:
            end = pd.to_datetime(end_date)
            filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], errors='coerce')
            filtered_df = filtered_df[filtered_df[date_col] <= end]
        except:
            pass
    
    if failure_class:
        class_col = get_column(filtered_df, ['arıza sınıfı', 'failure class'])
        if class_col:
            filtered_df = filtered_df[filtered_df[class_col].astype(str).str.startswith(failure_class)]
    
    # Excel dosyası oluştur
    project = session.get('current_project', 'belgrad')
    
    try:
        output = BytesIO()
        filtered_df.to_excel(output, sheet_name='FRACAS', index=False)
        output.seek(0)
        
        from flask import send_file
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'FRACAS_{project}_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
    except Exception as e:
        logger.error(f'Excel export hatası: {e}')
        flash('Excel export sırasında hata oluştu!', 'danger')
        return redirect(url_for('fracas.index'))


@bp.route('/export/pdf', methods=['GET'])
@login_required
def export_pdf():
    """FRACAS verileri PDF'ye aktar"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from io import BytesIO
        from flask import send_file
        
        df = load_fracas_data()
        
        if df is None:
            flash('FRACAS verileri bulunamadı!', 'danger')
            return redirect(url_for('fracas.index'))
        
        project = session.get('current_project', 'belgrad')
        
        # Filtre parametreleri
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        date_col = get_column(df, ['tarih', 'date', 'hata tarih'])
        filtered_df = df.copy()
        
        if start_date and date_col:
            try:
                start = pd.to_datetime(start_date)
                filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], errors='coerce')
                filtered_df = filtered_df[filtered_df[date_col] >= start]
            except:
                pass
        
        if end_date and date_col:
            try:
                end = pd.to_datetime(end_date)
                filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], errors='coerce')
                filtered_df = filtered_df[filtered_df[date_col] <= end]
            except:
                pass
        
        # PDF oluştur
        output = BytesIO()
        doc = SimpleDocTemplate(
            output,
            pagesize=landscape(A4),
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch
        )
        
        styles = getSampleStyleSheet()
        elements = []
        
        # Başlık
        title = Paragraph(f'<b>FRACAS Analiz Raporu - {project.upper()}</b>', styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # İstatistikler
        stats = calculate_basic_stats(filtered_df)
        stats_text = f"Toplam Arızalar: {stats['total_failures']} | Araçlar: {stats['unique_vehicles']} | Modüller: {stats['unique_modules']}"
        elements.append(Paragraph(stats_text, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Tablo - İlk 100 satır
        table_data = [list(filtered_df.columns)]
        for idx, row in filtered_df.head(100).iterrows():
            table_data.append([str(val)[:30] for val in row])  # Sütun genişliğini sınırla
        
        table = Table(table_data, colWidths=[1*inch if i == 0 else 0.5*inch for i in range(len(filtered_df.columns))])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
        ]))
        
        elements.append(table)
        
        doc.build(elements)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'FRACAS_{project}_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        logger.error(f'PDF export hatası: {e}')
        flash('PDF export sırasında hata oluştu!', 'danger')
        return redirect(url_for('fracas.index'))


@bp.route('/api/safety-analysis')
@login_required  
def api_safety_analysis():
    """API: Emniyet analizi"""
    df = load_fracas_data()
    if df is None:
        return jsonify({'error': 'Veri bulunamadı'}), 404
    
    # Emniyet sütununu bul
    safety_col = get_column(df, ['emniyet', 'safety', 'şiddet kategorisi', 'severity'])
    
    if not safety_col:
        return jsonify({'error': 'Emniyet kategorisi sütunu bulunamadı'}), 400
    
    safety_counts = df[safety_col].value_counts()
    
    result = []
    for category, count in safety_counts.items():
        result.append({
            'category': str(category),
            'count': int(count),
            'percentage': round(count / len(df) * 100, 1)
        })
    
    return jsonify(result)
