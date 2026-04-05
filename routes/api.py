"""
API Routes - RESTful API endpoints
JSON API'ler - Frontend ile veri alışverişi
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Equipment, Failure, Notification
from utils.api_helpers import api_success, api_error
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)
bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/projects', methods=['GET'])
@login_required
def projects() -> Dict[str, Any]:
    """Get user's accessible projects"""
    try:
        import json, os
        projects_list = current_user.get_assigned_projects()
        
        # Load projects from projects_config.json
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'projects_config.json')
        all_projects = []
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                all_projects = json.load(f).get('projects', [])
        
        if '*' in projects_list:
            projects_data = [{'code': p.get('code'), 'name': p.get('name')} for p in all_projects]
        else:
            projects_data = [
                {'code': p.get('code'), 'name': p.get('name')}
                for p in all_projects
                if p.get('code') in projects_list
            ]
        
        logger.info(f"Projeler listesi: {len(projects_data)} proje")
        return jsonify(projects_data)
        
    except Exception as e:
        logger.error(f"Projeler API hatası: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/failure-by-fracas-id', methods=['GET'])
@login_required
def failure_by_fracas_id() -> Dict[str, Any]:
    """Get failure by FRACAS ID"""
    try:
        fracas_id = request.args.get('fracas_id')
        
        if not fracas_id:
            return jsonify({'error': 'fracas_id required'}), 400
        
        failure = Failure.query.filter_by(fracas_id=fracas_id).first()
        
        if not failure:
            return jsonify({'error': 'Failure not found'}), 404
        
        if not current_user.can_access_project(failure.project_code):
            return jsonify({'error': 'Unauthorized'}), 403
        
        failure_data = {
            'id': failure.id,
            'fracas_id': failure.fracas_id,
            'equipment_code': failure.equipment.equipment_code if failure.equipment else '',
            'system': failure.system,
            'subsystem': failure.subsystem,
            'description': failure.description,
            'date_reported': failure.date_reported.isoformat() if failure.date_reported else '',
            'status': failure.status
        }
        
        logger.info(f"FRACAS arızası alındı: {fracas_id}")
        return jsonify(failure_data)
        
    except Exception as e:
        logger.error(f"Failure by FRACAS ID API hatası: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/equipment-parts', methods=['GET'])
@login_required
def equipment_parts() -> Dict[str, Any]:
    """Lookup spare parts by equipment"""
    try:
        equipment_code = request.args.get('equipment_code')
        
        if not equipment_code:
            return jsonify({'error': 'equipment_code required'}), 400
        
        equipment = Equipment.query.filter_by(equipment_code=equipment_code).first()
        
        if not equipment:
            return jsonify({'error': 'Equipment not found'}), 404
        
        if not current_user.can_access_project(equipment.project_code):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get parts from inventory
        from models import SparePartInventory
        parts = SparePartInventory.query.filter_by(equipment_id=equipment.id).all()
        
        parts_data = [
            {
                'id': p.id,
                'part_number': p.part_number,
                'description': p.description,
                'quantity': p.quantity,
                'unit': p.unit
            }
            for p in parts
        ]
        
        logger.info(f"Yedek parça arama: {equipment_code} -> {len(parts_data)} parça")
        return jsonify(parts_data)
        
    except Exception as e:
        logger.error(f"Parts lookup API hatası: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/statistics/<statistic_type>', methods=['GET'])
@login_required
def statistics(statistic_type: str) -> Dict[str, Any]:
    """Get statistics by type"""
    try:
        project_code = request.args.get('project', 'belgrad')
        
        if not current_user.can_access_project(project_code):
            return jsonify({'error': 'Unauthorized'}), 403
        
        if statistic_type == 'failures':
            failures = Failure.query.filter_by(project_code=project_code).count()
            return jsonify({'count': failures, 'type': 'failures'})
        
        elif statistic_type == 'equipment':
            equipment = Equipment.query.filter_by(project_code=project_code, parent_id=None).count()
            return jsonify({'count': equipment, 'type': 'equipment'})
        
        elif statistic_type == 'completion_rate':
            total = Failure.query.filter_by(project_code=project_code).count()
            completed = Failure.query.filter_by(project_code=project_code, status='closed').count()
            rate = (completed / total * 100) if total > 0 else 0
            return jsonify({'rate': rate, 'completed': completed, 'total': total})
        
        else:
            return jsonify({'error': 'Unknown statistic type'}), 400
        
    except Exception as e:
        logger.error(f"İstatistik API hatası: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/health', methods=['GET'])
def health() -> Dict[str, str]:
    """Health check endpoint
    ---
    tags:
      - System
    responses:
      200:
        description: Service is healthy
    """
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})


# ==================== TOPLU İŞLEMLER API ====================

@bp.route('/failures/bulk-status', methods=['POST'])
@login_required
def bulk_update_failure_status():
    """Toplu arıza durum güncelleme"""
    data = request.get_json(silent=True)
    if not data or not data.get('ids') or not data.get('status'):
        return api_error('ids ve status alanları gerekli', 400)
    
    valid_statuses = ['acik', 'devam_ediyor', 'cozuldu']
    new_status = data['status']
    if new_status not in valid_statuses:
        return api_error(f'Geçersiz durum: {new_status}', 400)
    
    ids = data['ids']
    if not isinstance(ids, list) or len(ids) > 100:
        return api_error('En fazla 100 kayıt güncellenebilir', 400)
    
    updated = Failure.query.filter(Failure.id.in_(ids)).update(
        {'status': new_status, 'updated_at': datetime.utcnow()},
        synchronize_session='fetch'
    )
    db.session.commit()
    
    logger.info(f"Bulk status update: {updated} failures -> {new_status} by user {current_user.id}")
    return api_success({'updated': updated}, f'{updated} arıza güncellendi')


@bp.route('/work-orders/bulk-status', methods=['POST'])
@login_required
def bulk_update_work_order_status():
    """Toplu iş emri durum güncelleme"""
    from models import WorkOrder
    
    data = request.get_json(silent=True)
    if not data or not data.get('ids') or not data.get('status'):
        return api_error('ids ve status alanları gerekli', 400)
    
    valid_statuses = ['beklemede', 'onay_bekliyor', 'devam_ediyor', 'tamamlandi', 'iptal']
    new_status = data['status']
    if new_status not in valid_statuses:
        return api_error(f'Geçersiz durum: {new_status}', 400)
    
    ids = data['ids']
    if not isinstance(ids, list) or len(ids) > 100:
        return api_error('En fazla 100 kayıt güncellenebilir', 400)
    
    update_data = {'status': new_status, 'updated_at': datetime.utcnow()}
    if new_status == 'tamamlandi':
        update_data['completed_date'] = datetime.utcnow()
    
    updated = WorkOrder.query.filter(WorkOrder.id.in_(ids)).update(
        update_data, synchronize_session='fetch'
    )
    db.session.commit()
    
    logger.info(f"Bulk status update: {updated} work orders -> {new_status} by user {current_user.id}")
    return api_success({'updated': updated}, f'{updated} iş emri güncellendi')


# ==================== BİLDİRİM API ====================

@bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Kullanıcının okunmamış bildirimlerini getir"""
    notifications = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).order_by(Notification.created_at.desc()).limit(20).all()
    
    return jsonify({
        'success': True,
        'count': len(notifications),
        'notifications': [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'category': n.category,
            'link': n.link,
            'created_at': n.created_at.isoformat() if n.created_at else None
        } for n in notifications]
    })


@bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Bildirimi okundu olarak işaretle"""
    notification = Notification.query.filter_by(
        id=notification_id, user_id=current_user.id
    ).first()
    if not notification:
        return api_error('Bildirim bulunamadı', 404)
    notification.is_read = True
    db.session.commit()
    return api_success(message='Bildirim okundu')


@bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Tüm bildirimleri okundu olarak işaretle"""
    Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).update({'is_read': True})
    db.session.commit()
    return api_success(message='Tüm bildirimler okundu')
