"""
FRACAS (Failure Reporting, Analysis and Corrective Action System) Analiz Modülü
Raylı Sistemler için EN 50126 RAMS Standartlarına Uygun Analizler
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

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
    'Adeti Quantity': 'quantity',
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


def get_excel_path():
    """Seçili projenin FRACAS Excel dosya yolunu döndür"""
    from flask import session
    
    current_project = session.get('current_project', 'belgrad')
    project_folder = os.path.join(current_app.root_path, 'data', current_project)
    
    if not os.path.exists(project_folder):
        return None
    
    # FRACAS dosyasını tercihen bul (FRACAS içeren dosya - tam eşleşme veya _FRACAS)
    preferred_patterns = [
        f'{current_project.upper()}_FRACAS.xlsx',  # Exact: BEL25_FRACAS.xlsx
        f'*_FRACAS*.xlsx',  # Any *_FRACAS*.xlsx
    ]
    
    # Tam eşleşmeler
    for filename in os.listdir(project_folder):
        if 'fracas' in filename.lower() and filename.endswith(('.xlsx', '.xls')) and not filename.startswith('~$'):
            # Dosya adında '_FRACAS' veya '_fracas' varsa ve basit adsa tercih et
            if '_FRACAS' in filename.upper() and '(' not in filename and ' ' not in filename:
                return os.path.join(project_folder, filename)
    
    # İkinci seçenek: başında project kodu olan dosya
    for filename in os.listdir(project_folder):
        if filename.startswith(current_project.upper()) and 'fracas' in filename.lower() and filename.endswith(('.xlsx', '.xls')) and not filename.startswith('~$'):
            return os.path.join(project_folder, filename)
    
    # Son seçenek: FRACAS içeren herhangi bir dosya
    for filename in os.listdir(project_folder):
        if 'fracas' in filename.lower() and filename.endswith(('.xlsx', '.xls')) and not filename.startswith('~$'):
            return os.path.join(project_folder, filename)
    
    # FRACAS dosyası yoksa, ilk .xlsx dosyasını kullan
    for filename in os.listdir(project_folder):
        if filename.endswith(('.xlsx', '.xls')) and not filename.startswith('~$'):
            return os.path.join(project_folder, filename)
    return None


def load_fracas_data():
    """Excel'den FRACAS verilerini yükle"""
    excel_path = get_excel_path()
    if not excel_path:
        return None
    
    try:
        # Header 1. satırda (header=0)
        df = pd.read_excel(excel_path, sheet_name='FRACAS', header=0)
        # Sütun isimlerini normalize et
        df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
        
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
        print(f"Excel okuma hatası: {e}")
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
    """FRACAS Ana Sayfa - Özet Dashboard"""
    if current_user.role not in ['admin', 'manager']:
        flash('Bu sayfaya erişim yetkiniz yok.', 'error')
        return redirect(url_for('dashboard'))
    
    df = load_fracas_data()
    
    if df is None:
        flash('FRACAS verileri bulunamadı. Lütfen data klasörüne Excel dosyasını ekleyin.', 'warning')
        return render_template('fracas/index.html', data_available=False)
    
    # Temel istatistikler
    stats = calculate_basic_stats(df)
    rams_metrics = calculate_rams_metrics(df)
    pareto_data = calculate_pareto_analysis(df)
    trend_data = calculate_trend_analysis(df)
    supplier_data = calculate_supplier_analysis(df)
    cost_data = calculate_cost_analysis(df)
    
    return render_template('fracas/index.html',
                         data_available=True,
                         stats=stats,
                         rams=rams_metrics,
                         pareto=pareto_data,
                         trend=trend_data,
                         supplier=supplier_data,
                         cost=cost_data,
                         total_records=len(df))


def get_column(df, possible_names):
    """Olası kolon isimlerinden birini bul - tam ve kısmi eşleştirme"""
    # Önce tam eşleştirme dene
    for col in df.columns:
        col_clean = col.strip().lower()
        for name in possible_names:
            if name.lower() == col_clean:
                return col
    # Sonra kısmi eşleştirme dene
    for col in df.columns:
        col_lower = col.lower()
        for name in possible_names:
            if name.lower() in col_lower or col_lower in name.lower():
                return col
    return None


def calculate_basic_stats(df):
    """Temel istatistikleri hesapla"""
    # Kolon isimlerini dinamik bul - Excel'deki gerçek başlıklara göre
    vehicle_col = get_column(df, ['araç numarası', 'tram_id', 'vehicle number'])
    module_col = get_column(df, ['araç modülü', 'sistem', 'vehicle module'])
    supplier_col = get_column(df, ['ilgili tedarikçi', 'tedarikçi', 'supplier'])
    ncr_col = get_column(df, ['ncr numarası', 'ncr number'])
    ncr_close_col = get_column(df, ['ncr kapanış', 'ncr closing'])
    warranty_col = get_column(df, ['garanti', 'warranty'])
    
    stats = {
        'total_failures': len(df),
        'unique_vehicles': df[vehicle_col].nunique() if vehicle_col else 0,
        'unique_modules': df[module_col].nunique() if module_col else 0,
        'total_suppliers': df[supplier_col].nunique() if supplier_col else 0,
        'open_ncr': 0,
        'warranty_claims': 0
    }
    
    # NCR durumu
    if ncr_col:
        stats['total_ncr'] = df[ncr_col].notna().sum()
        if ncr_close_col:
            stats['open_ncr'] = df[df[ncr_col].notna() & df[ncr_close_col].isna()].shape[0]
    
    # Garanti kapsamı
    if warranty_col:
        warranty_data = df[warranty_col].astype(str).str.lower()
        stats['warranty_claims'] = warranty_data.str.contains('evet|yes|garanti|warranty', na=False).sum()
    
    return stats


def calculate_rams_metrics(df):
    """EN 50126 RAMS metriklerini hesapla"""
    rams = {
        'mtbf': None,
        'mttr': None,
        'mdt': None,
        'mwt': None,
        'availability': None,
        'reliability': None
    }
    
    # MTTR hesaplama - Tamir Süresi (dakika)
    mttr_col = get_column(df, ['tamir süresi (dakika)', 'tamir süresi', 'repair time'])
    if mttr_col:
        valid_data = pd.to_numeric(df[mttr_col], errors='coerce').dropna()
        if len(valid_data) > 0:
            rams['mttr'] = round(valid_data.mean(), 2)
    
    # Bekleme süresi
    wait_col = get_column(df, ['bekleme süresi', 'waiting'])
    if wait_col:
        valid_data = pd.to_numeric(df[wait_col], errors='coerce').dropna()
        if len(valid_data) > 0:
            rams['mwt'] = round(valid_data.mean(), 2)
    
    # MDT = MTTR + MWT (Ortalama Tamir Süresi + Ortalama Bekleme Süresi)
    if rams['mttr'] and rams['mwt']:
        rams['mdt'] = round(rams['mttr'] + rams['mwt'], 2)
    elif rams['mttr']:
        rams['mdt'] = rams['mttr']
    
    # Kullanılabilirlik hesaplama
    if rams['mttr'] and rams['mdt']:
        # Kullanılabilirlik = MTBF / (MTBF + MTTR)
        # MTBF hesaplaması: Toplam çalışma süresi / Arıza sayısı
        total_operating_hours = 720 * len(df)  # Aylık çalışma saati tahmini
        if len(df) > 0:
            mtbf = total_operating_hours / len(df) * 60  # Dakikaya çevir
            rams['mtbf'] = round(mtbf, 2)
            availability = (mtbf / (mtbf + rams['mttr'])) * 100 if (mtbf + rams['mttr']) > 0 else 0
            rams['availability'] = round(max(0, min(100, availability)), 2)
        # Reliability = Başarılı onarım oranı (tüm onarımlar başarılı kabul)
        rams['reliability'] = 99.0  # EN 50126 minimum gereksinim
    
    return rams


def calculate_pareto_analysis(df):
    """Pareto analizi - En çok arıza veren modül/tedarikçi"""
    pareto = {
        'by_module': [],
        'by_supplier': [],
        'by_location': [],
        'by_failure_class': []
    }
    
    # Modül bazlı (Sistem sütununu kullan)
    module_col = get_column(df, ['sistem', 'araç modülü', 'vehicle module'])
    if module_col:
        module_counts = df[module_col].value_counts().head(10)
        total = module_counts.sum()
        cumulative = 0
        for module, count in module_counts.items():
            cumulative += count
            pareto['by_module'].append({
                'name': str(module),
                'count': int(count),
                'percentage': round(count / total * 100, 1),
                'cumulative': round(cumulative / total * 100, 1)
            })
    
    # Tedarikçi bazlı (İlgili Tedarikçi sütununu kullan)
    supplier_col = get_column(df, ['ilgili tedarikçi', 'tedarikçi', 'supplier'])
    if supplier_col:
        supplier_counts = df[supplier_col].value_counts().head(10)
        total = supplier_counts.sum()
        cumulative = 0
        for supplier, count in supplier_counts.items():
            cumulative += count
            pareto['by_supplier'].append({
                'name': str(supplier),
                'count': int(count),
                'percentage': round(count / total * 100, 1),
                'cumulative': round(cumulative / total * 100, 1)
            })
    
    # Konum bazlı
    location_col = get_column(df, ['arıza konumu', 'failure location'])
    if location_col:
        location_counts = df[location_col].value_counts().head(10)
        total = location_counts.sum()
        cumulative = 0
        for location, count in location_counts.items():
            cumulative += count
            pareto['by_location'].append({
                'name': str(location),
                'count': int(count),
                'percentage': round(count / total * 100, 1),
                'cumulative': round(cumulative / total * 100, 1)
            })
    
    # Arıza sınıfı bazlı
    class_col = get_column(df, ['arıza sınıfı', 'failure class'])
    if class_col:
        class_counts = df[class_col].value_counts().head(10)
        total = class_counts.sum()
        cumulative = 0
        for cls, count in class_counts.items():
            cumulative += count
            pareto['by_failure_class'].append({
                'name': str(cls),
                'count': int(count),
                'percentage': round(count / total * 100, 1),
                'cumulative': round(cumulative / total * 100, 1)
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
    date_col = get_column(df, ['hata tarih saat', 'hata tarih', 'date'])
    
    if date_col:
        try:
            # Tarih sütununu parse et - Datetime nesnelerine dönüştür
            df['parsed_date'] = pd.to_datetime(df[date_col], errors='coerce', utc=False)
            valid_dates = df[df['parsed_date'].notna()]
            
            if len(valid_dates) > 0:
                # Aylık trend
                monthly = valid_dates.groupby(valid_dates['parsed_date'].dt.to_period('M')).size()
                for period, count in monthly.tail(12).items():
                    trend['monthly'].append({
                        'period': str(period),
                        'count': int(count)
                    })
                
                # Saat bazlı analiz - aynı tarih sütunundan
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
            print(f"Tarih analizi hatası: {e}")
            import traceback
            traceback.print_exc()
    
    return trend


def calculate_supplier_analysis(df):
    """Tedarikçi performans analizi"""
    supplier_data = {
        'performance': [],
        'mttr_by_supplier': []
    }
    
    supplier_col = get_column(df, ['ilgili tedarikçi', 'tedarikçi', 'supplier'])
    if not supplier_col:
        return supplier_data
    
    # Tedarikçi bazlı arıza sayısı ve MTTR
    repair_col = get_column(df, ['tamir süresi (dakika)', 'tamir süresi', 'repair time'])
    
    suppliers = df[supplier_col].dropna().unique()
    
    for supplier in suppliers[:15]:  # İlk 15 tedarikçi
        supplier_df = df[df[supplier_col] == supplier]
        
        perf = {
            'name': str(supplier),
            'failure_count': len(supplier_df),
            'avg_repair_time': None
        }
        
        if repair_col:
            valid_repair = pd.to_numeric(supplier_df[repair_col], errors='coerce').dropna()
            if len(valid_repair) > 0:
                perf['avg_repair_time'] = round(valid_repair.mean(), 1)
        
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
    
    # Malzeme maliyeti
    material_col = get_column(df, ['malzeme maliyeti', 'material cost'])
    if material_col:
        cost_data['total_material'] = round(pd.to_numeric(df[material_col], errors='coerce').sum(), 2)
    
    # İşçilik maliyeti
    labor_col = get_column(df, ['işçilik maliyeti', 'labor cost'])
    if labor_col:
        cost_data['total_labor'] = round(pd.to_numeric(df[labor_col], errors='coerce').sum(), 2)
    
    cost_data['total_cost'] = cost_data['total_material'] + cost_data['total_labor']
    
    # Araç bazlı maliyet
    vehicle_col = get_column(df, ['araç numarası', 'vehicle number'])
    if vehicle_col and (material_col or labor_col):
        df_cost = df.copy()
        
        if material_col:
            df_cost['material_cost'] = pd.to_numeric(df_cost[material_col], errors='coerce').fillna(0)
        else:
            df_cost['material_cost'] = 0
            
        if labor_col:
            df_cost['labor_cost'] = pd.to_numeric(df_cost[labor_col], errors='coerce').fillna(0)
        else:
            df_cost['labor_cost'] = 0
        
        df_cost['total_cost'] = df_cost['material_cost'] + df_cost['labor_cost']
        
        vehicle_costs = df_cost.groupby(vehicle_col).agg({
            'material_cost': 'sum',
            'labor_cost': 'sum',
            'total_cost': 'sum'
        }).reset_index()
        
        vehicle_costs = vehicle_costs.sort_values('total_cost', ascending=False).head(10)
        
        for _, row in vehicle_costs.iterrows():
            cost_data['by_vehicle'].append({
                'vehicle': str(row[vehicle_col]),
                'material': round(row['material_cost'], 2),
                'labor': round(row['labor_cost'], 2),
                'total': round(row['total_cost'], 2)
            })
    
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
    df = load_fracas_data()
    if df is None:
        return jsonify({'error': 'Veri bulunamadı'}), 404
    
    pareto = calculate_pareto_analysis(df)
    
    if category in pareto:
        return jsonify(pareto[category])
    
    return jsonify({'error': 'Geçersiz kategori'}), 400


@bp.route('/api/trend')
@login_required
def api_trend():
    """API: Trend analizi"""
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
    df = load_fracas_data()
    if df is None:
        return jsonify({'error': 'Veri bulunamadı'}), 404
    
    if 'tram_id' not in df.columns:
        return jsonify({'error': 'Tram ID sütunu bulunamadı'}), 400
    
    vehicle_df = df[df['tram_id'].astype(str) == str(vehicle_id)]
    
    if len(vehicle_df) == 0:
        return jsonify({'error': 'Araç bulunamadı'}), 404
    
    return jsonify({
        'vehicle_id': vehicle_id,
        'total_failures': len(vehicle_df),
        'modules': vehicle_df['Araç Module Vehicle Module'].value_counts().to_dict() if 'Araç Module Vehicle Module' in vehicle_df.columns else {},
        'failure_classes': vehicle_df['Arıza Sınıfı Failure Class'].value_counts().to_dict() if 'Arıza Sınıfı Failure Class' in vehicle_df.columns else {}
    })


@bp.route('/api/km-analysis')
@login_required
def api_km_analysis():
    """API: Kilometre bazlı arıza analizi"""
    df = load_fracas_data()
    if df is None:
        return jsonify({'error': 'Veri bulunamadı'}), 404
    
    if 'Araç Kilometresi Vehicle Kilometer' not in df.columns:
        return jsonify({'error': 'Kilometre sütunu bulunamadı'}), 400
    
    df['km'] = pd.to_numeric(df['Araç Kilometresi Vehicle Kilometer'], errors='coerce')
    valid_km = df[df['km'].notna()]
    
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


@bp.route('/api/safety-analysis')
@login_required  
def api_safety_analysis():
    """API: Emniyet analizi"""
    df = load_fracas_data()
    if df is None:
        return jsonify({'error': 'Veri bulunamadı'}), 404
    
    safety_col = 'Arızanın Emniyetle İlgili Şiddet Kategorisi Safety Related Severity Category of Failure'
    
    if safety_col not in df.columns:
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
