from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import db, Equipment, WorkOrder, KPI, Failure
from sqlalchemy import func
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
    
    return render_template('dashboard/index.html',
                         equipment_summary=equipment_summary,
                         wo_summary=wo_summary,
                         critical_work_orders=critical_work_orders,
                         upcoming_maintenance=upcoming_maintenance,
                         recent_failures=recent_failures,
                         latest_kpi=latest_kpi)


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
