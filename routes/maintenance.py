from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_required, current_user
from models import db, MaintenancePlan, Equipment, MaintenanceLog, WorkOrder
from datetime import datetime
import pandas as pd
import os

bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')


def load_trams_from_file(project_code=None):
    """Veriler.xlsx Sayfa2'den tramvay listesini yükle"""
    if project_code is None:
        project_code = session.get('current_project', 'belgrad')
    
    veriler_path = os.path.join(current_app.root_path, 'data', project_code, 'Veriler.xlsx')
    
    if not os.path.exists(veriler_path):
        # Fallback: Equipment tablosundan çek
        return [eq.equipment_code for eq in Equipment.query.filter_by(parent_id=None).all()]
    
    try:
        df = pd.read_excel(veriler_path, sheet_name='Sayfa2', header=0)
        if 'tram_id' in df.columns:
            tram_list = df['tram_id'].dropna().unique().tolist()
            # String dönüştür ve sıra
            tram_list = [str(t) for t in tram_list]
            tram_list.sort(key=lambda x: int(x) if x.isdigit() else 0)
            return tram_list
        # Fallback: Equipment tablosundan çek
        return [eq.equipment_code for eq in Equipment.query.filter_by(parent_id=None).all()]
    except Exception as e:
        print(f"Veriler.xlsx okuma hatası ({project_code}): {e}")
        # Fallback: Equipment tablosundan çek
        return [eq.equipment_code for eq in Equipment.query.filter_by(parent_id=None).all()]


@bp.route('/plans')
@login_required
def plans():
    """Bakım planları listesi"""
    maintenance_type = request.args.get('type', 'all')
    current_project = session.get('current_project', 'belgrad')
    project_name = session.get('project_name', 'Proje Seçilmedi')
    
    # Tramvay listesini trams.xlsx'den al
    tramvaylar = load_trams_from_file(current_project)
    
    query = MaintenancePlan.query.filter_by(is_active=True)
    
    if maintenance_type != 'all':
        query = query.filter_by(maintenance_type=maintenance_type)
    
    plans = query.order_by(MaintenancePlan.plan_name).all()
    
    return render_template('maintenance/plans.html', 
                          plans=plans, 
                          tramvaylar=tramvaylar,
                          project_name=project_name)


@bp.route('/plan/<int:plan_id>')
@login_required
def plan_detail(plan_id):
    """Bakım planı detayları"""
    plan = MaintenancePlan.query.get_or_404(plan_id)
    
    # Bu plana bağlı iş emirleri
    work_orders = plan.work_orders.order_by(WorkOrder.scheduled_start.desc()).limit(20).all()
    
    return render_template('maintenance/plan_detail.html', plan=plan, work_orders=work_orders)


@bp.route('/logs')
@login_required
def logs():
    """Bakım kayıtları"""
    page = request.args.get('page', 1, type=int)
    
    logs = MaintenanceLog.query.order_by(
        MaintenanceLog.log_date.desc()
    ).paginate(page=page, per_page=50, error_out=False)
    
    return render_template('maintenance/logs.html', logs=logs)


@bp.route('/log/<int:log_id>')
@login_required
def log_detail(log_id):
    """Bakım kaydı detayları"""
    log = MaintenanceLog.query.get_or_404(log_id)
    return render_template('maintenance/log_detail.html', log=log)


@bp.route('/add-log/<int:work_order_id>', methods=['GET', 'POST'])
@login_required
def add_log(work_order_id):
    """Bakım kaydı ekleme"""
    work_order = WorkOrder.query.get_or_404(work_order_id)
    
    # Yetki kontrolü
    if current_user.role == 'technician' and work_order.assigned_to != current_user.id:
        flash('Bu işlem için yetkiniz yok.', 'error')
        return redirect(url_for('workorder.detail', work_order_id=work_order_id))
    
    if request.method == 'POST':
        action_taken = request.form.get('action_taken')
        observations = request.form.get('observations')
        duration_hours = request.form.get('duration_hours', type=float)
        cost = request.form.get('cost', type=float)
        
        new_log = MaintenanceLog(
            work_order_id=work_order_id,
            equipment_id=work_order.equipment_id,
            technician_id=current_user.id,
            action_taken=action_taken,
            observations=observations,
            duration_hours=duration_hours,
            cost=cost
        )
        
        db.session.add(new_log)
        
        # Ekipmanın son bakım tarihini güncelle
        equipment = work_order.equipment
        equipment.last_maintenance_date = datetime.utcnow()
        
        db.session.commit()
        
        flash('Bakım kaydı eklendi.', 'success')
        return redirect(url_for('workorder.detail', work_order_id=work_order_id))
    
    return render_template('maintenance/add_log.html', work_order=work_order)
