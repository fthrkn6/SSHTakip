"""
FRACAS Analiz Dashboard - EN 15341 Bakım KPI Standardına Uygun
Gelişmiş Arıza & Bakım Analitikleri
Bozankaya SSH Takip Sistemi
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session, send_file, current_app
from flask_login import login_required, current_user
from models import db, Equipment, WorkOrder, Failure
from datetime import datetime, timedelta
from utils.utils_performance import CacheManager, CacheConfig
import os
import json
import pandas as pd
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

bp = Blueprint('kpi', __name__, url_prefix='/kpi')


def get_fracas_data(project=None):
    """Seçili projenin FRACAS verilerini yükle"""
    from flask import current_app
    
    try:
        if project is None:
            project = session.get('current_project', 'belgrad')
        
        ariza_listesi_dir = os.path.join(current_app.root_path, 'logs', project, 'ariza_listesi')
        
        if os.path.exists(ariza_listesi_dir):
            for filename in os.listdir(ariza_listesi_dir):
                if filename.upper().startswith('FRACAS_') and filename.endswith('.xlsx') and not filename.startswith('~$'):
                    filepath = os.path.join(ariza_listesi_dir, filename)
                    try:
                        df = pd.read_excel(filepath, sheet_name='FRACAS', header=3)
                        df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
                        
                        # Veri temizliği
                        df = df[df['FRACAS ID'].notna()]
                        return df
                    except Exception as e:
                        logger.error(f'Excel okuma hatasi ({filename}): {e}')
                        continue
    except Exception as e:
        logger.error(f'get_fracas_data hatasi: {e}')
    
    return None


def apply_filters(df, start_date=None, end_date=None, vehicle=None, system=None, failure_class=None):
    """FRACAS verilerine filtre uygula"""
    if df is None or df.empty:
        return None
    
    filtered_df = df.copy()
    
    # Tarih kolonu bul
    date_col = None
    for col in df.columns:
        if 'tarih' in col.lower() and 'hata' in col.lower():
            date_col = col
            break
    
    # Tarih filtresi
    if date_col and start_date:
        try:
            filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], errors='coerce')
            start = pd.to_datetime(start_date)
            filtered_df = filtered_df[filtered_df[date_col] >= start]
        except (ValueError, TypeError) as e:
            logger.warning(f'Tarih filtresi hatası (start_date): {e}')
    
    if date_col and end_date:
        try:
            end = pd.to_datetime(end_date)
            filtered_df = filtered_df[filtered_df[date_col] <= end]
        except (ValueError, TypeError) as e:
            logger.warning(f'Tarih filtresi hatası (end_date): {e}')
    
    # Araç filtresi
    if vehicle:
        vehicle_col = None
        for col in df.columns:
            if 'araç' in col.lower() and 'numarası' in col.lower():
                vehicle_col = col
                break
        if vehicle_col:
            filtered_df = filtered_df[filtered_df[vehicle_col].astype(str).str.contains(str(vehicle), na=False)]
    
    # Sistem filtresi
    if system:
        if 'Sistem' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Sistem'].astype(str).str.contains(str(system), na=False, case=False)]
    
    # Arıza Sınıfı filtresi
    if failure_class:
        for col in filtered_df.columns:
            if 'arıza sınıfı' in col.lower():
                filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(str(failure_class), na=False)]
                break
    
    return filtered_df if not filtered_df.empty else None


def calculate_mtbf_mttr(df):
    """MTBF ve MTTR hesapla"""
    if df is None or df.empty:
        return {'mtbf': 0, 'mtbf_time': None, 'mttr': 0, 'total_downtime': 0}
    
    result = {'mtbf': 0, 'mtbf_time': None, 'mttr': 0, 'total_downtime': 0}
    
    # MTTR - Tamir Süresi (dakika)
    repair_col = None
    for col in df.columns:
        if 'tamir süresi' in col.lower():
            repair_col = col
            break
    
    if repair_col:
        try:
            df[repair_col] = pd.to_numeric(df[repair_col], errors='coerce')
            valid_mttr = df[repair_col].dropna()
            if len(valid_mttr) > 0:
                result['mttr'] = round(valid_mttr.mean(), 2)
                result['total_downtime'] = round(valid_mttr.sum(), 1)
        except (ValueError, TypeError):
            pass
    
    # MTBF - Araç KM bazında
    vehicle_col = None
    km_col = None
    for col in df.columns:
        if 'araç numarası' in col.lower():
            vehicle_col = col
        if 'araç kilometresi' in col.lower():
            km_col = col
    
    if vehicle_col and km_col:
        try:
            df[km_col] = pd.to_numeric(df[km_col], errors='coerce')
            vehicle_mtbf = []
            for vehicle in df[vehicle_col].dropna().unique():
                v_data = df[df[vehicle_col] == vehicle][km_col].dropna()
                if len(v_data) > 1:
                    km_range = v_data.max() - v_data.min()
                    if km_range > 0:
                        mtbf_val = km_range / len(v_data)
                        vehicle_mtbf.append(mtbf_val)
            if vehicle_mtbf:
                result['mtbf'] = round(sum(vehicle_mtbf) / len(vehicle_mtbf), 0)
        except (ValueError, TypeError):
            pass
    
    # MTBF - Zaman bazlı (tarihlerden hesapla)
    date_col = None
    for col in df.columns:
        if 'tarih' in col.lower():
            date_col = col
            break
    
    if date_col and vehicle_col:
        try:
            dates = pd.to_datetime(df[date_col], errors='coerce').dropna()
            if len(dates) >= 2:
                date_range_days = (dates.max() - dates.min()).days
                if date_range_days > 0:
                    total_vehicles = max(df[vehicle_col].nunique(), 1)
                    # Araç başına operasyon dakikası / toplam arıza sayısı
                    total_op_minutes = date_range_days * 16 * 60 * total_vehicles
                    result['mtbf_time'] = round(total_op_minutes / len(df), 2)
        except (ValueError, TypeError):
            pass
    
    return result


def calculate_availability_reliability(df, total_downtime_hours):
    """Availability ve Reliability hesapla"""
    if df is None or df.empty:
        return {'availability': None, 'reliability': None}
    
    vehicle_col = None
    for col in df.columns:
        if 'araç numarası' in col.lower():
            vehicle_col = col
            break
    
    vehicle_count = df[vehicle_col].nunique() if vehicle_col else 1
    
    # Operasyon parametrelerini projects_config.json'dan oku
    op_days = 300
    op_hours = 16
    try:
        config_path = os.path.join(current_app.root_path, 'projects_config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        defaults = config.get('defaults', {})
        op_days = defaults.get('operational_days_per_year', 300)
        op_hours = defaults.get('operational_hours_per_day', 16)
    except Exception:
        pass
    
    yearly_op_hours = op_days * op_hours * max(vehicle_count, 1)
    
    availability = max(0, round((yearly_op_hours - total_downtime_hours) / yearly_op_hours * 100, 1)) if total_downtime_hours > 0 else 98.5
    availability = min(availability, 100)
    reliability = min(availability + 2, 99.9)
    
    return {'availability': availability, 'reliability': reliability}


def calculate_data_quality(df):
    """Veri kalitesi kontrolü - kritik kolonlardaki doluluk oranını hesapla"""
    if df is None or df.empty:
        return {'score': 0, 'details': [], 'total_rows': 0}
    
    critical_keywords = [
        ('Araç No', 'araç numarası'),
        ('Tarih', 'tarih'),
        ('Tamir Süresi', 'tamir süresi'),
        ('KM', 'araç kilometresi'),
        ('Sistem', 'sistem'),
    ]
    
    total_rows = len(df)
    details = []
    filled_scores = []
    
    for label, keyword in critical_keywords:
        found_col = None
        for col in df.columns:
            if keyword in col.lower():
                found_col = col
                break
        if found_col:
            non_null = df[found_col].dropna().count()
            fill_rate = round((non_null / total_rows) * 100, 1) if total_rows > 0 else 0
            details.append({'column': label, 'fill_rate': fill_rate, 'found': True})
            filled_scores.append(fill_rate)
        else:
            details.append({'column': label, 'fill_rate': 0, 'found': False})
            filled_scores.append(0)
    
    overall_score = round(sum(filled_scores) / len(filled_scores), 1) if filled_scores else 0
    return {'score': overall_score, 'details': details, 'total_rows': total_rows}


def get_analysis_data(df):
    """Tüm analiz verilerini hesapla"""
    if df is None or df.empty:
        return get_empty_analysis()
    
    result = {
        'total_failures': len(df),
        'unique_vehicles': 0,
        'unique_systems': 0,
        'kpi': {},
        'failure_by_source': {},
        'failure_by_class': {},
        'failure_by_system': {},
        'failure_by_type': {},
        'top_vehicles': [],
        'top_parts': [],
        'top_suppliers': [],
        'monthly_trend': [],
        'repair_personnel': {}
    }
    
    try:
        # Temel metrikler
        vehicle_col = None
        for col in df.columns:
            if 'araç numarası' in col.lower():
                vehicle_col = col
                break
        if vehicle_col:
            result['unique_vehicles'] = df[vehicle_col].nunique()
        
        if 'Sistem' in df.columns:
            result['unique_systems'] = df['Sistem'].nunique()
        
        # KPI Hesapları
        result['kpi'] = calculate_mtbf_mttr(df)
        result['kpi'].update(calculate_availability_reliability(df, result['kpi']['total_downtime']))
        
        # Arıza Kaynağı
        for col in df.columns:
            if 'arıza kaynağı' in col.lower():
                source_counts = df[col].value_counts().head(10).to_dict()
                result['failure_by_source'] = {str(k): int(v) for k, v in source_counts.items() if pd.notna(k)}
                break
        
        # Arıza Sınıfı
        for col in df.columns:
            if 'arıza sınıfı' in col.lower():
                class_counts = df[col].value_counts().head(10).to_dict()
                result['failure_by_class'] = {str(k): int(v) for k, v in class_counts.items() if pd.notna(k)}
                break
        
        # Sistem bazında arızalar
        if 'Sistem' in df.columns:
            system_counts = df['Sistem'].value_counts().head(10).to_dict()
            result['failure_by_system'] = {str(k): int(v) for k, v in system_counts.items() if pd.notna(k)}
        
        # Arıza Tipi
        for col in df.columns:
            if 'arıza tipi' in col.lower():
                type_counts = df[col].value_counts().head(10).to_dict()
                result['failure_by_type'] = {str(k): int(v) for k, v in type_counts.items() if pd.notna(k)}
                break
        
        # En çok arıza yapan araçlar
        if vehicle_col:
            top_vehicles = df[vehicle_col].value_counts().head(5)
            result['top_vehicles'] = [{'vehicle': str(v), 'count': int(c)} for v, c in top_vehicles.items()]
        
        # En sık değiştirilen parçalar
        for col in df.columns:
            if 'parça adı' in col.lower():
                top_parts = df[col].value_counts().head(5)
                result['top_parts'] = [{'part': str(v) if pd.notna(v) else 'Bilinmiyor', 'count': int(c)} for v, c in top_parts.items()]
                break
        
        # En sık arızan tedarikçiler
        for col in df.columns:
            if 'tedarikçi' in col.lower():
                top_suppliers = df[col].value_counts().head(5)
                result['top_suppliers'] = [{'supplier': str(v) if pd.notna(v) else 'Bilinmiyor', 'count': int(c)} for v, c in top_suppliers.items()]
                break
        
        # Aylık trend
        date_col = None
        for col in df.columns:
            if 'tarih' in col.lower() and 'hata' in col.lower():
                date_col = col
                break
        
        if date_col:
            try:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                monthly = df[date_col].dt.to_period('M').value_counts().sort_index().tail(12)
                result['monthly_trend'] = [{'month': str(m), 'count': int(c)} for m, c in monthly.items()]
            except (ValueError, TypeError):
                pass
        
        # Tamir için gerekli personel
        for col in df.columns:
            if 'personel' in col.lower() or 'personel sayısı' in col.lower():
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    personnel_counts = df[col].value_counts().head(5).to_dict()
                    result['repair_personnel'] = {str(int(k)): int(v) for k, v in personnel_counts.items() if pd.notna(k)}
                except (ValueError, TypeError):
                    pass
                break
        
    except Exception as e:
        logger.error(f'Analiz hesaplama hatasi: {e}')
    
    return result


def get_empty_analysis():
    """Boş analiz verilerini döndür"""
    return {
        'total_failures': 0,
        'unique_vehicles': 0,
        'unique_systems': 0,
        'kpi': {'mtbf': 0, 'mtbf_time': None, 'mttr': 0, 'availability': None, 'reliability': None, 'total_downtime': 0},
        'failure_by_source': {},
        'failure_by_class': {},
        'failure_by_system': {},
        'failure_by_type': {},
        'top_vehicles': [],
        'top_parts': [],
        'top_suppliers': [],
        'monthly_trend': [],
        'repair_personnel': {}
    }


@bp.route('/')
@login_required
def index():
    """FRACAS Analiz Dashboard"""
    try:
        current_project = session.get('current_project', 'belgrad')
        project_name = session.get('project_name', 'Belgrad')
        
        if current_user.role not in ['admin', 'muhendis', 'manager']:
            flash('Bu sayfaya erişim yetkiniz yok.', 'error')
            return redirect(url_for('dashboard.index'))
        
        # FRACAS verilerini yükle
        df = get_fracas_data(current_project)
        
        # Filtreler
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        vehicle = request.args.get('vehicle')
        system = request.args.get('system')
        failure_class = request.args.get('failure_class')
        
        # Filtreleri uygula
        filtered_df = apply_filters(df, start_date, end_date, vehicle, system, failure_class)
        
        # Cache key oluştur
        cache_key = f"kpi:{current_project}:{start_date}:{end_date}:{vehicle}:{system}:{failure_class}"
        
        # Önce cache'den dene
        try:
            from app import cache_manager
            cached = cache_manager.get(cache_key)
            if cached is not None:
                analysis = cached
                data_available = True
            else:
                raise ValueError("cache miss")
        except Exception:
            # Cache miss veya cache yoksa hesapla
            if filtered_df is not None:
                analysis = get_analysis_data(filtered_df)
                data_available = True
                # Sonucu cache'e kaydet (1 saat TTL)
                try:
                    from app import cache_manager
                    cache_manager.set(cache_key, analysis, CacheConfig.TTL_MEDIUM)
                except Exception:
                    pass
            else:
                analysis = get_empty_analysis()
                data_available = False
        
        # Sistemler listesi (filtreleme için)
        systems = []
        if df is not None and not df.empty and 'Sistem' in df.columns:
            systems = sorted([s for s in df['Sistem'].dropna().unique() if pd.notna(s)])
        
        # Araçlar listesi
        vehicles = []
        if df is not None and not df.empty:
            for col in df.columns:
                if 'araç numarası' in col.lower():
                    vehicles = sorted([str(v) for v in df[col].dropna().unique() if pd.notna(v)])
                    break
        
        # Veri kalitesi analizi
        data_quality = calculate_data_quality(df)
        
        return render_template('kpi/dashboard.html',
                             current_project=current_project,
                             project_name=project_name,
                             analysis=analysis,
                             systems=systems,
                             vehicles=vehicles,
                             data_quality=data_quality,
                             filters={
                                 'start_date': start_date,
                                 'end_date': end_date,
                                 'vehicle': vehicle,
                                 'system': system,
                                 'failure_class': failure_class
                             },
                             data_available=data_available)
    
    except Exception as e:
        logger.error(f'KPI index hatasi: {e}')
        flash('KPI sayfası yüklenirken hata oluştu.', 'error')
        return redirect(url_for('dashboard.index'))


@bp.route('/export/excel')
@login_required
def export_excel():
    """Verileri Excel'e indir"""
    try:
        current_project = session.get('current_project', 'belgrad')
        df = get_fracas_data(current_project)
        
        # Filtreler
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        vehicle = request.args.get('vehicle')
        system = request.args.get('system')
        
        filtered_df = apply_filters(df, start_date, end_date, vehicle, system)
        
        if filtered_df is None or filtered_df.empty:
            flash('İndirilebilir veri yok.', 'warning')
            return redirect(url_for('kpi.index'))
        
        # Excel dosyası oluştur
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, sheet_name='FRACAS Verileri', index=False)
            
            # Özet sayfası
            analysis = get_analysis_data(filtered_df)
            summary_data = {
                'Metrik': [
                    'Toplam Arızalar',
                    'Eşsiz Araçlar',
                    'Sistem Sayısı',
                    'MTBF (km)',
                    'MTTR (dakika)',
                    'Availability (%)',
                    'Reliability (%)',
                    'Toplam Downtime (dakika)'
                ],
                'Değer': [
                    analysis['total_failures'],
                    analysis['unique_vehicles'],
                    analysis['unique_systems'],
                    int(analysis['kpi']['mtbf']),
                    f"{analysis['kpi']['mttr']:.2f}",
                    f"{analysis['kpi']['availability']:.1f}",
                    f"{analysis['kpi']['reliability']:.1f}",
                    int(analysis['kpi']['total_downtime'])
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Özet', index=False)
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'FRACAS_Analiz_{current_project}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except Exception as e:
        logger.error(f'Excel export hatasi: {e}')
        flash('Excel export başarısız.', 'error')
        return redirect(url_for('kpi.index'))


@bp.route('/api/filters')
@login_required
def api_filters():
    """Filtreleme seçeneklerini API'de döndür"""
    try:
        current_project = session.get('current_project', 'belgrad')
        df = get_fracas_data(current_project)
        
        if df is None or df.empty:
            return jsonify({'success': False})
        
        # Sistemler
        systems = []
        if 'Sistem' in df.columns:
            systems = sorted([str(s) for s in df['Sistem'].dropna().unique() if pd.notna(s)])
        
        # Araçlar
        vehicles = []
        for col in df.columns:
            if 'araç numarası' in col.lower():
                vehicles = sorted([str(v) for v in df[col].dropna().unique() if pd.notna(v)])
                break
        
        # Arıza Sınıfları
        failure_classes = []
        for col in df.columns:
            if 'arıza sınıfı' in col.lower():
                failure_classes = sorted([str(c) for c in df[col].dropna().unique() if pd.notna(c)])
                break
        
        return jsonify({
            'success': True,
            'systems': systems,
            'vehicles': vehicles,
            'failure_classes': failure_classes
        })
    
    except Exception as e:
        logger.error(f'Filtreleme API hatasi: {e}')
        return jsonify({'success': False})
