"""
API Routes - RESTful API endpoints
JSON API'ler - Frontend ile veri alışverişi
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Equipment, Failure
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
        projects_list = current_user.get_assigned_projects()
        
        if '*' in projects_list:
            # Admin: all projects
            from config import Config
            all_projects = Config.PROJECTS if hasattr(Config, 'PROJECTS') else []
            projects_data = [{'code': p.get('code'), 'name': p.get('name')} for p in all_projects]
        else:
            # Regular user: assigned projects only
            from config import Config
            all_projects = Config.PROJECTS if hasattr(Config, 'PROJECTS') else []
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


@bp.route('/parts-lookup', methods=['GET'])
@login_required
def parts_lookup() -> Dict[str, Any]:
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
    """Health check endpoint - no authentication required"""
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})
