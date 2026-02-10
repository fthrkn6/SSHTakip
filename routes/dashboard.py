from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import db, Equipment, WorkOrder, KPI, Failure, ServiceLog, ServiceStatus
from sqlalchemy import func, desc
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('/')
@login_required
def index():
    """Ana dashboard - Genel bakış"""
    
    # Ekipman durumu özeti
    equipment_stats = db.session.query(
        Equipment.status,
        func.count(Equipment.id)
    ).filter_by(parent_id=None).group_by(Equipment.status).all()
    
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
    ).order_by(WorkOrder.scheduled_start).limit(10).all()
    
    # Yaklaşan bakımlar (7 gün içinde)
    upcoming_maintenance = WorkOrder.query.filter(
        WorkOrder.status.in_(['pending', 'scheduled']),
        WorkOrder.scheduled_start >= datetime.utcnow(),
        WorkOrder.scheduled_start <= datetime.utcnow() + timedelta(days=7)
    ).order_by(WorkOrder.scheduled_start).limit(10).all()
    
    # Son arızalar
    recent_failures = Failure.query.filter_by(
        resolved=False
    ).order_by(Failure.failure_date.desc()).limit(5).all()
    
    # Son KPI'lar
    latest_kpi = KPI.query.filter(
        KPI.equipment_id.is_(None)  # Genel KPI'lar
    ).order_by(KPI.calculation_date.desc()).first()
    
    # ===== Tramvay Filosu - ServiceStatus'ten Veri Çek (DOĞRU KAYNAK) =====
    # Tüm tramvayları getir
    tramvaylar = Equipment.query.filter_by(parent_id=None).all()
    
    # ServiceStatus'ten bugünün verilerini al
    today = str(date.today())
    service_status_records = ServiceStatus.query.filter_by(date=today).all()
    
    # ServiceStatus'i dict'e dönüştür
    status_dict = {record.tram_id: record.status for record in service_status_records}
    
    # Her tramvay için durumunu belirle
    tramvay_statuses = []
    for tramvay in tramvaylar:
        # ServiceStatus'ten durum al
        status_from_db = status_dict.get(tramvay.equipment_code, 'Servis')
        
        # Durum kategorize et
        if status_from_db == 'Servis':
            status_display = 'aktif'
        elif status_from_db == 'İşletme Kaynaklı Servis Dışı':
            status_display = 'bakim'
        else:  # 'Servis Dışı'
            status_display = 'ariza'
        
        tramvay_statuses.append({
            'id': tramvay.id,
            'equipment_code': tramvay.equipment_code,
            'name': tramvay.name,
            'location': tramvay.location if hasattr(tramvay, 'location') else '',
            'total_km': tramvay.total_km if hasattr(tramvay, 'total_km') else 0,
            'status': status_display,
            'status_db': status_from_db
        })
    
    # Açık arızaları getir
    son_arizalar = Failure.query.filter_by(resolved=False).order_by(
        desc(Failure.failure_date)
    ).limit(20).all()
    
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
    
    stats = {
        'total_tramvay': len(tramvay_statuses),
        'aktif_servis': aktif_count,
        'bakimda': bakim_count,
        'arizali': ariza_count,
        'aktif_ariza': len(son_arizalar),
        'bekleyen_is_emri': wo_summary.get('pending', 0),
        'devam_eden_is_emri': wo_summary.get('in_progress', 0),
        'bugun_tamamlanan': wo_summary.get('completed', 0),
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
                         kpi=latest_kpi)


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
