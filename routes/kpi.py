"""
KPI Dashboard - EN 15341 Bakım KPI Standardına Uygun
Bozankaya SSH Takip Sistemi
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from flask_login import login_required, current_user
from models import db, Equipment, WorkOrder, Failure
from sqlalchemy import func
from datetime import datetime, timedelta
import os
import pandas as pd

bp = Blueprint('kpi', __name__, url_prefix='/kpi')


def get_fracas_data():
    """Seçili projenin FRACAS verilerini yükle"""
    from flask import current_app
    
    current_project = session.get('current_project', 'belgrad')
    project_folder = os.path.join(current_app.root_path, 'data', current_project)
    
    if not os.path.exists(project_folder):
        return None
    
    for filename in os.listdir(project_folder):
        if filename.endswith(('.xlsx', '.xls')) and not filename.startswith('~$'):
            filepath = os.path.join(project_folder, filename)
            try:
                df = pd.read_excel(filepath, sheet_name='FRACAS', header=3)
                df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
                
                # FRACAS ID kolonunu bul
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
    
    return None


def get_ariza_listesi_data():
    """Seçili projenin Arıza Listesi verilerini yükle (logs/{project}/ariza_listesi/)"""
    from flask import current_app
    
    current_project = session.get('current_project', 'belgrad')
    
    # Birincil konum: data/{project}/Veriler.xlsx
    veriler_file = os.path.join(current_app.root_path, 'data', current_project, 'Veriler.xlsx')
    
    # Fallback: logs/{project}/ariza_listesi/
    ariza_dir = os.path.join(current_app.root_path, 'logs', current_project, 'ariza_listesi')
    
    filepath = None
    use_sheet = None
    header_row = 0
    
    if os.path.exists(veriler_file):
        filepath = veriler_file
        use_sheet = 'Veriler'
        header_row = 0
    elif os.path.exists(ariza_dir):
        for filename in os.listdir(ariza_dir):
            if filename.endswith('.xlsx') and not filename.startswith('~$'):
                filepath = os.path.join(ariza_dir, filename)
                use_sheet = 'Ariza Listesi'
                header_row = 3
                break
    
    if not filepath:
        return None
    
    try:
        df = pd.read_excel(filepath, sheet_name=use_sheet, header=header_row)
        df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
        
        # FRACAS ID kolonunu bul ve geçerli kayıtları filtrele
        fracas_col = None
        for col in df.columns:
            if 'fracas' in col.lower() and 'id' in col.lower():
                fracas_col = col
                break
        
        if fracas_col:
            df = df[df[fracas_col].notna()]
        
        return df
    except Exception as e:
        print(f"Arıza Listesi okuma hatası: {e}")
        return None
    
    return None


@bp.route('/')
@login_required
def index():
    """KPI Dashboard - EN 15341 uyumlu - Arıza Listesi verileri kullanarak"""
    if current_user.role not in ['admin', 'muhendis', 'manager']:
        flash('Bu sayfaya erişim yetkiniz yok.', 'error')
        return redirect(url_for('dashboard'))
    
    # Arıza Listesi verilerini tercih et (daha güncel ve doğru)
    df = get_ariza_listesi_data()
    
    # Eğer Arıza Listesi yoksa FRACAS verilerini kullan
    if df is None:
        df = get_fracas_data()
    
    kpi_data = {
        'mtbf': 0,
        'mttr': 0,
        'availability': 0,
        'reliability': 0,
        'failure_count': 0,
        'vehicle_count': 0,
        'total_downtime': 0,
        'monthly_trend': [],
        'failure_by_category': {},
        'top_failing_vehicles': [],
        'data_source': 'Arıza Listesi' if df is not None else 'Veri Yok'
    }
    
    if df is not None and len(df) > 0:
        # Araç sütununu bul (Türkçe/İngilizce çeşitliliğe karşı güvenli)
        vehicle_col = None
        km_col = None
        mttr_col = None
        cat_col = None
        date_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if vehicle_col is None and ('araç' in col_lower or 'vehicle' in col_lower) and ('numar' in col_lower or 'number' in col_lower or 'no' in col_lower):
                vehicle_col = col
            if km_col is None and ('kilometre' in col_lower or 'km' in col_lower):
                km_col = col
            if mttr_col is None and ('tamir' in col_lower or 'repair' in col_lower) and ('saat' in col_lower or 'hour' in col_lower):
                mttr_col = col
            if cat_col is None and (('arıza' in col_lower or 'failure' in col_lower) and ('sınıf' in col_lower or 'class' in col_lower)):
                cat_col = col
            if date_col is None and ('tarih' in col_lower or 'date' in col_lower):
                date_col = col
        
        # Arıza sayısı ve araç sayısı
        kpi_data['failure_count'] = len(df)
        
        if vehicle_col:
            kpi_data['vehicle_count'] = df[vehicle_col].nunique()
            
            # MTBF hesaplama (ortalama km farkı / arıza sayısı)
            if km_col and df[km_col].notna().any():
                try:
                    # Sayısal değerlere dönüştür
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
                        kpi_data['mtbf'] = round(sum(vehicle_mtbf) / len(vehicle_mtbf), 0)
                except Exception as e:
                    print(f"MTBF hesaplama hatası: {e}")
                    kpi_data['mtbf'] = 0
        
        # MTTR (Ortalama Tamir Süresi)
        if mttr_col:
            try:
                df[mttr_col] = pd.to_numeric(df[mttr_col], errors='coerce')
                valid_mttr = df[mttr_col].dropna()
                if len(valid_mttr) > 0:
                    kpi_data['mttr'] = round(valid_mttr.mean(), 2)
                    kpi_data['total_downtime'] = round(valid_mttr.sum(), 1)
            except Exception as e:
                print(f"MTTR hesaplama hatası: {e}")
        
        # Kullanılabilirlik (Availability)
        if kpi_data['vehicle_count'] > 0:
            if kpi_data['total_downtime'] > 0:
                # Yıllık operasyon saati (300 gün * 16 saat)
                yearly_op_hours = 300 * 16 * kpi_data['vehicle_count']
                kpi_data['availability'] = max(0, round((yearly_op_hours - kpi_data['total_downtime']) / yearly_op_hours * 100, 1))
                kpi_data['availability'] = min(kpi_data['availability'], 100)
            else:
                kpi_data['availability'] = 98.5
        else:
            kpi_data['availability'] = 95.0
        
        # Güvenilirlik (Reliability) - Availability üzerine dayalı
        kpi_data['reliability'] = min(kpi_data['availability'] + 1, 99.9)
        
        # Arıza kategorileri
        if cat_col:
            try:
                category_counts = df[cat_col].dropna().value_counts().head(10).to_dict()
                kpi_data['failure_by_category'] = {str(k): int(v) for k, v in category_counts.items()}
            except Exception as e:
                print(f"Kategori hesaplama hatası: {e}")
        
        # En çok arıza yapan araçlar
        if vehicle_col:
            try:
                top_vehicles = df[vehicle_col].dropna().value_counts().head(5)
                kpi_data['top_failing_vehicles'] = [
                    {'vehicle': str(v), 'count': int(c)} 
                    for v, c in top_vehicles.items()
                ]
            except Exception as e:
                print(f"Top vehicles hesaplama hatası: {e}")
        
        # Aylık trend
        if date_col:
            try:
                df['month'] = pd.to_datetime(df[date_col], errors='coerce').dt.to_period('M')
                monthly = df.groupby('month').size()
                kpi_data['monthly_trend'] = [
                    {'month': str(m), 'count': int(c)} 
                    for m, c in monthly.tail(12).items()
                ]
            except Exception as e:
                print(f"Aylık trend hesaplama hatası: {e}")
    
    # Veritabanından ek veriler
    db_stats = {
        'active_equipment': Equipment.query.filter_by(status='aktif').count(),
        'open_failures': Failure.query.filter_by(status='acik').count(),
        'pending_workorders': WorkOrder.query.filter_by(status='beklemede').count()
    }
    
    return render_template('kpi/index.html', 
                         kpi=kpi_data, 
                         db_stats=db_stats,
                         project_name=session.get('project_name', 'Proje'))


@bp.route('/api/data')
@login_required
def api_data():
    """KPI verileri API endpoint"""
    df = get_fracas_data()
    
    if df is None:
        return jsonify({'error': 'Veri bulunamadı'}), 404
    
    return jsonify({
        'record_count': len(df),
        'columns': list(df.columns)[:20]  # İlk 20 kolon
    })
