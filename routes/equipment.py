"""
Equipment & Failure Management Routes
Ekipman ve Arızaların Web dostu API ve GUI'leri
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Equipment, Failure
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)
bp = Blueprint('equipment', __name__, url_prefix='/equipment')


@bp.route('/listesi')
@login_required
def listesi():
    """Equipment list page"""
    try:
        project_code = request.args.get('project', current_user.get_assigned_projects()[0] if current_user.get_assigned_projects() else 'belgrad')
        
        if not current_user.can_access_project(project_code):
            flash('Bu projeye erişim yetkiniz yok.', 'error')
            return redirect(url_for('dashboard.index'))
        
        # Get all equipment for project
        equipment_list = Equipment.query.filter_by(
            project_code=project_code,
            parent_id=None
        ).all()
        
        logger.info(f"Equipment listesi yüklendi: {len(equipment_list)} kayıt ({project_code})")
        return render_template('equipment/listesi.html', equipment=equipment_list, project_code=project_code)
        
    except Exception as e:
        logger.error(f"Equipment listesi hatası: {e}")
        flash(f'Hata: {str(e)}', 'danger')
        return redirect(url_for('dashboard.index'))


@bp.route('/<int:id>')
@login_required
def detay(id: int):
    """Equipment detail page"""
    try:
        equipment = Equipment.query.get(id)
        
        if not equipment:
            flash('Equipment bulunamadı.', 'warning')
            return redirect(url_for('equipment.listesi'))
        
        if not current_user.can_access_project(equipment.project_code):
            flash('Bu projeye erişim yetkiniz yok.', 'error')
            return redirect(url_for('dashboard.index'))
        
        # Get related failures
        failures = Failure.query.filter_by(equipment_id=id).all()
        
        logger.info(f"Equipment detayı görüntülendi: {equipment.equipment_code}")
        return render_template('equipment/detay.html', equipment=equipment, failures=failures)
        
    except Exception as e:
        logger.error(f"Equipment detay hatası: {e}")
        flash(f'Hata: {str(e)}', 'danger')
        return redirect(url_for('equipment.listesi'))


@bp.route('/api/sync', methods=['POST'])
@login_required
def api_sync():
    """Sync equipment from Excel"""
    try:
        if not current_user.is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        project_code = request.json.get('project')
        
        if not current_user.can_access_project(project_code):
            return jsonify({'error': 'Unauthorized'}), 403
        
        from utils.utils_equipment_sync import sync_equipment_with_excel
        created, updated = sync_equipment_with_excel(project_code)
        
        logger.info(f"Equipment senkronize: {created} yeni, {updated} güncellenmiş")
        return jsonify({
            'success': True,
            'created': created,
            'updated': updated
        })
        
    except Exception as e:
        logger.error(f"Equipment senkronizasyon hatası: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/km', methods=['GET'])
@login_required
def api_km() -> Dict[str, Any]:
    """Get equipment KM data"""
    try:
        project_code = request.args.get('project', 'belgrad')
        
        if not current_user.can_access_project(project_code):
            return jsonify({'error': 'Unauthorized'}), 403
        
        from utils.utils_km_manager import KMDataManager
        km_data = KMDataManager.get_all_tram_kms(project_code)
        
        logger.info(f"KM verileri yüklendi: {len(km_data)} araç")
        return jsonify(km_data)
        
    except Exception as e:
        logger.error(f"KM API hatası: {e}")
        return jsonify({'error': str(e)}), 500
