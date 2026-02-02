from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, WorkOrder, Equipment, MaintenancePlan, User
from datetime import datetime

bp = Blueprint('workorder', __name__, url_prefix='/workorder')


@bp.route('/')
@login_required
def index():
    """İş emirleri listesi"""
    status = request.args.get('status', 'all')
    priority = request.args.get('priority', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = WorkOrder.query
    
    # Teknisyenler sadece kendilerine atanan emirleri görür
    if current_user.role == 'technician':
        query = query.filter_by(assigned_to=current_user.id)
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    if priority != 'all':
        query = query.filter_by(priority=priority)
    
    work_orders = query.order_by(
        WorkOrder.priority.desc(), 
        WorkOrder.scheduled_start
    ).paginate(page=page, per_page=50, error_out=False)
    
    return render_template('workorder/index.html', work_orders=work_orders)


@bp.route('/<int:work_order_id>')
@login_required
def detail(work_order_id):
    """İş emri detayları"""
    work_order = WorkOrder.query.get_or_404(work_order_id)
    
    # Yetki kontrolü
    if current_user.role == 'technician' and work_order.assigned_to != current_user.id:
        flash('Bu iş emrini görüntüleme yetkiniz yok.', 'error')
        return redirect(url_for('workorder.index'))
    
    return render_template('workorder/detail.html', work_order=work_order)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Yeni iş emri oluşturma"""
    if current_user.role not in ['admin', 'manager', 'operator']:
        flash('İş emri oluşturma yetkiniz yok.', 'error')
        return redirect(url_for('workorder.index'))
    
    if request.method == 'POST':
        equipment_id = request.form.get('equipment_id', type=int)
        title = request.form.get('title')
        description = request.form.get('description')
        work_type = request.form.get('work_type')
        priority = request.form.get('priority', 'medium')
        scheduled_start = request.form.get('scheduled_start')
        assigned_to = request.form.get('assigned_to', type=int)
        
        # İş emri numarası oluştur
        last_wo = WorkOrder.query.order_by(WorkOrder.id.desc()).first()
        wo_number = f"WO-{datetime.utcnow().strftime('%Y%m')}-{(last_wo.id + 1) if last_wo else 1:04d}"
        
        new_wo = WorkOrder(
            work_order_number=wo_number,
            equipment_id=equipment_id,
            title=title,
            description=description,
            work_type=work_type,
            priority=priority,
            status='pending',
            created_by=current_user.id,
            assigned_to=assigned_to if assigned_to else None
        )
        
        if scheduled_start:
            new_wo.scheduled_start = datetime.fromisoformat(scheduled_start)
        
        db.session.add(new_wo)
        db.session.commit()
        
        flash(f'İş emri {wo_number} oluşturuldu.', 'success')
        return redirect(url_for('workorder.detail', work_order_id=new_wo.id))
    
    # Form için veriler
    equipment = Equipment.query.filter_by(parent_id=None).all()
    technicians = User.query.filter_by(role='technician', is_active=True).all()
    
    return render_template('workorder/create.html', 
                         equipment=equipment, 
                         technicians=technicians)


@bp.route('/<int:work_order_id>/update-status', methods=['POST'])
@login_required
def update_status(work_order_id):
    """İş emri durumu güncelleme"""
    work_order = WorkOrder.query.get_or_404(work_order_id)
    
    # Yetki kontrolü
    if current_user.role == 'technician' and work_order.assigned_to != current_user.id:
        flash('Bu işlem için yetkiniz yok.', 'error')
        return redirect(url_for('workorder.detail', work_order_id=work_order_id))
    
    new_status = request.form.get('status')
    
    if new_status == 'in_progress' and not work_order.actual_start:
        work_order.actual_start = datetime.utcnow()
    elif new_status == 'completed':
        work_order.actual_end = datetime.utcnow()
        work_order.completion_notes = request.form.get('completion_notes')
        work_order.actual_cost = request.form.get('actual_cost', type=float)
    
    work_order.status = new_status
    db.session.commit()
    
    flash('İş emri durumu güncellendi.', 'success')
    return redirect(url_for('workorder.detail', work_order_id=work_order_id))
