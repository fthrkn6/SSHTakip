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


@bp.route('/')
@login_required
def index():
    """KPI Dashboard - EN 15341 uyumlu"""
    if current_user.role not in ['admin', 'muhendis', 'manager']:
        flash('Bu sayfaya erişim yetkiniz yok.', 'error')
        return redirect(url_for('dashboard'))
    
    # Excel verilerini yükle
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
        'top_failing_vehicles': []
    }
    
    if df is not None and len(df) > 0:
        # Araç sayısı
        vehicle_col = None
        for col in df.columns:
            if 'araç' in col.lower() and 'numar' in col.lower():
                vehicle_col = col
                break
        
        kpi_data['vehicle_count'] = df[vehicle_col].nunique() if vehicle_col else 0
        kpi_data['failure_count'] = len(df)
        
        # MTTR (Ortalama tamir süresi)
        mttr_col = None
        for col in df.columns:
            if 'tamir süresi' in col.lower() and 'saat' in col.lower():
                mttr_col = col
                break
        
        if mttr_col and df[mttr_col].notna().any():
            kpi_data['mttr'] = round(df[mttr_col].mean(), 2)
            kpi_data['total_downtime'] = round(df[mttr_col].sum(), 1)
        
        # MTBF hesaplama (Toplam km / Arıza sayısı)
        km_col = None
        for col in df.columns:
            if 'kilometre' in col.lower():
                km_col = col
                break
        
        if km_col and vehicle_col and df[km_col].notna().any():
            # Her araç için MTBF
            vehicle_mtbf = []
            for vehicle in df[vehicle_col].unique():
                v_data = df[df[vehicle_col] == vehicle]
                if len(v_data) > 1:
                    km_diff = v_data[km_col].max() - v_data[km_col].min()
                    if km_diff > 0:
                        vehicle_mtbf.append(km_diff / len(v_data))
            
            if vehicle_mtbf:
                kpi_data['mtbf'] = round(sum(vehicle_mtbf) / len(vehicle_mtbf), 0)
        
        # Kullanılabilirlik (Availability) - Basit hesaplama
        # Varsayım: Günde 16 saat operasyon
        if kpi_data['vehicle_count'] > 0 and kpi_data['total_downtime'] > 0:
            # Yıllık operasyon saati (300 gün * 16 saat)
            yearly_op_hours = 300 * 16 * kpi_data['vehicle_count']
            kpi_data['availability'] = round((yearly_op_hours - kpi_data['total_downtime']) / yearly_op_hours * 100, 1)
        else:
            kpi_data['availability'] = 95.0  # Varsayılan
        
        # Güvenilirlik
        kpi_data['reliability'] = min(kpi_data['availability'] + 2, 99.9)
        
        # Arıza kategorileri
        cat_col = None
        for col in df.columns:
            if 'arıza sınıfı' in col.lower() or 'failure class' in col.lower():
                cat_col = col
                break
        
        if cat_col:
            category_counts = df[cat_col].value_counts().head(10).to_dict()
            kpi_data['failure_by_category'] = {str(k): int(v) for k, v in category_counts.items()}
        
        # En çok arıza yapan araçlar
        if vehicle_col:
            top_vehicles = df[vehicle_col].value_counts().head(5)
            kpi_data['top_failing_vehicles'] = [
                {'vehicle': str(v), 'count': int(c)} 
                for v, c in top_vehicles.items()
            ]
        
        # Aylık trend
        date_col = None
        for col in df.columns:
            if 'tarih' in col.lower() and 'date' in col.lower():
                date_col = col
                break
        
        if date_col:
            try:
                df['month'] = pd.to_datetime(df[date_col], errors='coerce').dt.to_period('M')
                monthly = df.groupby('month').size()
                kpi_data['monthly_trend'] = [
                    {'month': str(m), 'count': int(c)} 
                    for m, c in monthly.tail(12).items()
                ]
            except:
                pass
    
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
