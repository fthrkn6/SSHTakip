from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Equipment, MaintenanceLog, WorkOrder, SensorData, Failure
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('equipment', __name__, url_prefix='/equipment')


@bp.route('/')
@login_required
def index():
    """Ekipman listesi"""
    equipment_type = request.args.get('type', 'all')
    status = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    query = Equipment.query.filter_by(parent_id=None)  # Sadece ana ekipmanlar
    
    if equipment_type != 'all':
        query = query.filter_by(equipment_type=equipment_type)
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    equipment_list = query.order_by(Equipment.equipment_code).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('equipment/index.html', equipment=equipment_list)


@bp.route('/<int:equipment_id>')
@login_required
def detail(equipment_id):
    """Ekipman detayları ve dijital ikiz"""
    equipment = Equipment.query.get_or_404(equipment_id)
    
    # Alt bileşenler
    components = equipment.children.all()
    
    # Son bakım kayıtları
    recent_maintenance = equipment.maintenance_logs.order_by(
        MaintenanceLog.log_date.desc()
    ).limit(10).all()
    
    # Aktif iş emirleri
    active_work_orders = equipment.work_orders.filter(
        WorkOrder.status.in_(['pending', 'scheduled', 'in_progress'])
    ).all()
    
    # Son 24 saat sensör verileri
    sensor_data = equipment.sensor_data.filter(
        SensorData.timestamp >= datetime.utcnow() - timedelta(days=1)
    ).order_by(SensorData.timestamp.desc()).all()
    
    # Arıza geçmişi
    failures = equipment.failures.order_by(Failure.failure_date.desc()).limit(10).all()
    
    return render_template('equipment/detail.html',
                         equipment=equipment,
                         components=components,
                         recent_maintenance=recent_maintenance,
                         active_work_orders=active_work_orders,
                         sensor_data=sensor_data,
                         failures=failures)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Yeni ekipman ekleme"""
    if current_user.role not in ['admin', 'manager']:
        flash('Bu işlem için yetkiniz yok.', 'error')
        return redirect(url_for('equipment.index'))
    
    if request.method == 'POST':
        equipment_code = request.form.get('equipment_code')
        name = request.form.get('name')
        equipment_type = request.form.get('equipment_type')
        manufacturer = request.form.get('manufacturer')
        model = request.form.get('model')
        serial_number = request.form.get('serial_number')
        location = request.form.get('location')
        criticality = request.form.get('criticality', 'medium')
        parent_id = request.form.get('parent_id', type=int)
        
        # Kod benzersizliği kontrolü
        if Equipment.query.filter_by(equipment_code=equipment_code).first():
            flash('Bu ekipman kodu zaten kullanılıyor.', 'error')
            return redirect(url_for('equipment.add'))
        
        new_equipment = Equipment(
            equipment_code=equipment_code,
            name=name,
            equipment_type=equipment_type,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial_number,
            location=location,
            criticality=criticality,
            parent_id=parent_id if parent_id else None
        )
        
        db.session.add(new_equipment)
        db.session.commit()
        
        flash(f'{name} ekipmanı başarıyla eklendi.', 'success')
        return redirect(url_for('equipment.detail', equipment_id=new_equipment.id))
    
    # Ana ekipmanlar (parent seçimi için)
    parent_equipment = Equipment.query.filter_by(parent_id=None).all()
    
    return render_template('equipment/add.html', parent_equipment=parent_equipment)


@bp.route('/<int:equipment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(equipment_id):
    """Ekipman düzenleme"""
    if current_user.role not in ['admin', 'manager']:
        flash('Bu işlem için yetkiniz yok.', 'error')
        return redirect(url_for('equipment.detail', equipment_id=equipment_id))
    
    equipment = Equipment.query.get_or_404(equipment_id)
    
    if request.method == 'POST':
        equipment.name = request.form.get('name')
        equipment.equipment_type = request.form.get('equipment_type')
        equipment.manufacturer = request.form.get('manufacturer')
        equipment.model = request.form.get('model')
        equipment.location = request.form.get('location')
        equipment.status = request.form.get('status')
        equipment.criticality = request.form.get('criticality')
        
        db.session.commit()
        
        flash(f'{equipment.name} başarıyla güncellendi.', 'success')
        return redirect(url_for('equipment.detail', equipment_id=equipment_id))
    
    return render_template('equipment/edit.html', equipment=equipment)


@bp.route('/api/sensor-data/<int:equipment_id>')
@login_required
def sensor_data_api(equipment_id):
    """Sensör verileri API - Grafik için"""
    hours = request.args.get('hours', 24, type=int)
    sensor_type = request.args.get('sensor_type', 'all')
    
    query = SensorData.query.filter_by(equipment_id=equipment_id).filter(
        SensorData.timestamp >= datetime.utcnow() - timedelta(hours=hours)
    )
    
    if sensor_type != 'all':
        query = query.filter_by(sensor_type=sensor_type)
    
    data = query.order_by(SensorData.timestamp).all()
    
    result = [{
        'timestamp': d.timestamp.isoformat(),
        'sensor_type': d.sensor_type,
        'value': d.value,
        'unit': d.unit,
        'is_anomaly': d.is_anomaly
    } for d in data]
    
    return jsonify(result)
