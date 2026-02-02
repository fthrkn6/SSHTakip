from flask import Blueprint, jsonify, request
from flask_login import login_required
from models import db, Equipment, WorkOrder, KPI, SensorData, MaintenanceLog
from datetime import datetime, timedelta

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/v1/equipment', methods=['GET'])
@login_required
def get_equipment():
    """Ekipman listesi API"""
    equipment_type = request.args.get('type')
    status = request.args.get('status')
    
    query = Equipment.query
    
    if equipment_type:
        query = query.filter_by(equipment_type=equipment_type)
    
    if status:
        query = query.filter_by(status=status)
    
    equipment = query.all()
    
    result = [{
        'id': e.id,
        'equipment_code': e.equipment_code,
        'name': e.name,
        'type': e.equipment_type,
        'status': e.status,
        'location': e.location,
        'criticality': e.criticality
    } for e in equipment]
    
    return jsonify(result)


@bp.route('/v1/equipment/<int:equipment_id>', methods=['GET'])
@login_required
def get_equipment_detail(equipment_id):
    """Ekipman detay API"""
    equipment = Equipment.query.get_or_404(equipment_id)
    
    result = {
        'id': equipment.id,
        'equipment_code': equipment.equipment_code,
        'name': equipment.name,
        'type': equipment.equipment_type,
        'manufacturer': equipment.manufacturer,
        'model': equipment.model,
        'serial_number': equipment.serial_number,
        'status': equipment.status,
        'location': equipment.location,
        'criticality': equipment.criticality,
        'total_operating_hours': equipment.total_operating_hours,
        'total_distance_km': equipment.total_distance_km,
        'last_maintenance_date': equipment.last_maintenance_date.isoformat() if equipment.last_maintenance_date else None,
        'next_maintenance_date': equipment.next_maintenance_date.isoformat() if equipment.next_maintenance_date else None
    }
    
    return jsonify(result)


@bp.route('/v1/work-orders', methods=['GET'])
@login_required
def get_work_orders():
    """İş emirleri listesi API"""
    status = request.args.get('status')
    priority = request.args.get('priority')
    
    query = WorkOrder.query
    
    if status:
        query = query.filter_by(status=status)
    
    if priority:
        query = query.filter_by(priority=priority)
    
    work_orders = query.order_by(WorkOrder.created_at.desc()).limit(100).all()
    
    result = [{
        'id': wo.id,
        'work_order_number': wo.work_order_number,
        'title': wo.title,
        'status': wo.status,
        'priority': wo.priority,
        'equipment_id': wo.equipment_id,
        'scheduled_start': wo.scheduled_start.isoformat() if wo.scheduled_start else None,
        'created_at': wo.created_at.isoformat()
    } for wo in work_orders]
    
    return jsonify(result)


@bp.route('/v1/sensor-data', methods=['POST'])
@login_required
def post_sensor_data():
    """Sensör verisi gönderme API - IoT cihazlar için"""
    data = request.json
    
    try:
        sensor_data = SensorData(
            equipment_id=data['equipment_id'],
            sensor_type=data['sensor_type'],
            sensor_location=data.get('sensor_location'),
            value=data['value'],
            unit=data.get('unit'),
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.utcnow()
        )
        
        db.session.add(sensor_data)
        db.session.commit()
        
        return jsonify({'success': True, 'id': sensor_data.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/v1/kpi/latest', methods=['GET'])
@login_required
def get_latest_kpi():
    """En son KPI verileri API"""
    equipment_id = request.args.get('equipment_id', type=int)
    
    query = KPI.query
    
    if equipment_id:
        query = query.filter_by(equipment_id=equipment_id)
    else:
        query = query.filter(KPI.equipment_id.is_(None))
    
    kpi = query.order_by(KPI.calculation_date.desc()).first()
    
    if not kpi:
        return jsonify({'error': 'KPI not found'}), 404
    
    result = {
        'calculation_date': kpi.calculation_date.isoformat(),
        'mtbf': kpi.mtbf,
        'mttr': kpi.mttr,
        'availability': kpi.availability,
        'reliability': kpi.reliability,
        'maintenance_cost': kpi.maintenance_cost,
        'total_downtime_hours': kpi.total_downtime_hours
    }
    
    return jsonify(result)


@bp.route('/v1/health', methods=['GET'])
def health_check():
    """Sistem sağlık kontrolü"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })
