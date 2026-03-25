"""
Maintenance & Work Order Management Routes
Bakım Planları ve İş Emirleri Yönetimi
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, MaintenancePlan, WorkOrder, Equipment
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)
bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')


@bp.route('/planlar')
@login_required
def planlar():
    """Maintenance plans list page"""
    try:
        project_code = request.args.get('project', current_user.get_assigned_projects()[0] if current_user.get_assigned_projects() else 'belgrad')
        
        if not current_user.can_access_project(project_code):
            flash('Bu projeye erişim yetkiniz yok.', 'error')
            return redirect(url_for('dashboard.index'))
        
        # Get maintenance plans
        plans = MaintenancePlan.query.filter_by(project_code=project_code).all()
        
        logger.info(f"Bakım planları yüklendi: {len(plans)} kayıt ({project_code})")
        return render_template('maintenance/planlar.html', plans=plans, project_code=project_code)
        
    except Exception as e:
        logger.error(f"Bakım planları hatası: {e}")
        flash(f'Hata: {str(e)}', 'danger')
        return redirect(url_for('dashboard.index'))


@bp.route('/plan/ekle', methods=['GET', 'POST'])
@login_required
def plan_ekle():
    """Add new maintenance plan"""
    try:
        if not current_user.is_admin():
            flash('Bu işlem için yetkiniz yok.', 'error')
            return redirect(url_for('maintenance.planlar'))
        
        if request.method == 'POST':
            # Get form data
            equipment_id = request.form.get('equipment_id')
            maintenance_type = request.form.get('maintenance_type')
            frequency_days = request.form.get('frequency_days')
            description = request.form.get('description')
            
            # Create new maintenance plan
            plan = MaintenancePlan(
                equipment_id=equipment_id,
                maintenance_type=maintenance_type,
                frequency_days=int(frequency_days),
                description=description,
                next_due_date=datetime.utcnow(),
                status='active'
            )
            
            db.session.add(plan)
            db.session.commit()
            
            logger.info(f"Bakım planı oluşturuldu: {plan.id}")
            flash('Bakım planı başarıyla oluşturuldu.', 'success')
            return redirect(url_for('maintenance.planlar'))
        
        # Get equipment list
        project_code = current_user.get_assigned_projects()[0] if current_user.get_assigned_projects() else 'belgrad'
        equipment = Equipment.query.filter_by(project_code=project_code).all()
        
        return render_template('maintenance/plan_ekle.html', equipment=equipment)
        
    except Exception as e:
        logger.error(f"Bakım planı ekleme hatası: {e}")
        flash(f'Hata: {str(e)}', 'danger')
        return redirect(url_for('maintenance.planlar'))


@bp.route('/emirler')
@login_required
def emirler():
    """Work orders list page"""
    try:
        project_code = request.args.get('project', current_user.get_assigned_projects()[0] if current_user.get_assigned_projects() else 'belgrad')
        
        if not current_user.can_access_project(project_code):
            flash('Bu projeye erişim yetkiniz yok.', 'error')
            return redirect(url_for('dashboard.index'))
        
        # Get work orders
        work_orders = WorkOrder.query.filter_by(project_code=project_code).all()
        
        logger.info(f"İş emirleri yüklendi: {len(work_orders)} kayıt ({project_code})")
        return render_template('maintenance/emirler.html', work_orders=work_orders, project_code=project_code)
        
    except Exception as e:
        logger.error(f"İş emirleri hatası: {e}")
        flash(f'Hata: {str(e)}', 'danger')
        return redirect(url_for('dashboard.index'))


@bp.route('/emir/ekle', methods=['GET', 'POST'])
@login_required
def emir_ekle():
    """Add new work order"""
    try:
        if request.method == 'POST':
            # Get form data
            equipment_id = request.form.get('equipment_id')
            work_type = request.form.get('work_type')
            description = request.form.get('description')
            assigned_to = request.form.get('assigned_to')
            estimated_hours = request.form.get('estimated_hours')
            
            # Create new work order
            work_order = WorkOrder(
                equipment_id=equipment_id,
                work_type=work_type,
                description=description,
                assigned_to_id=assigned_to,
                estimated_hours=float(estimated_hours),
                status='pending',
                created_by=current_user.id,
                created_at=datetime.utcnow()
            )
            
            db.session.add(work_order)
            db.session.commit()
            
            logger.info(f"İş emri oluşturuldu: {work_order.id}")
            flash('İş emri başarıyla oluşturuldu.', 'success')
            return redirect(url_for('maintenance.emirler'))
        
        # Get equipment and technician list
        from models import User
        project_code = current_user.get_assigned_projects()[0] if current_user.get_assigned_projects() else 'belgrad'
        equipment = Equipment.query.filter_by(project_code=project_code).all()
        technicians = User.query.filter(User.role.in_(['technician', 'mechanic'])).all()
        
        return render_template('maintenance/emir_ekle.html', equipment=equipment, technicians=technicians)
        
    except Exception as e:
        logger.error(f"İş emri ekleme hatası: {e}")
        flash(f'Hata: {str(e)}', 'danger')
        return redirect(url_for('maintenance.emirler'))


@bp.route('/api/tablosu')
@login_required
def api_tablosu() -> Dict[str, Any]:
    """Get maintenance data as JSON"""
    try:
        project_code = request.args.get('project', 'belgrad')
        
        if not current_user.can_access_project(project_code):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get maintenance plans and work orders
        plans = MaintenancePlan.query.filter_by(project_code=project_code).all()
        work_orders = WorkOrder.query.filter_by(project_code=project_code).all()
        
        plans_data = [
            {
                'id': p.id,
                'equipment': p.equipment.equipment_code if p.equipment else '',
                'type': p.maintenance_type,
                'frequency': p.frequency_days,
                'next_due': p.next_due_date.isoformat() if p.next_due_date else '',
                'status': p.status
            }
            for p in plans
        ]
        
        orders_data = [
            {
                'id': wo.id,
                'equipment': wo.equipment.equipment_code if wo.equipment else '',
                'type': wo.work_type,
                'status': wo.status,
                'estimated_hours': wo.estimated_hours,
                'created_at': wo.created_at.isoformat() if wo.created_at else ''
            }
            for wo in work_orders
        ]
        
        logger.info(f"Bakım verileri yüklendi: {len(plans_data)} plan, {len(orders_data)} emir")
        return jsonify({'plans': plans_data, 'orders': orders_data})
        
    except Exception as e:
        logger.error(f"Bakım API hatası: {e}")
        return jsonify({'error': str(e)}), 500
