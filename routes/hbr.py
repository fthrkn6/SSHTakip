"""
HBR (Hazlanan Bakım Raporu) Routes - Hazırlanan Bakım Raporu Yönetimi
EN 13306 Standardına Uygun Bakım Planlama
"""

from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db
import os
import logging
from datetime import datetime
from typing import Optional, Tuple

logger = logging.getLogger(__name__)
bp = Blueprint('hbr', __name__, url_prefix='/hbr')


@bp.route('/listesi')
@login_required
def listesi():
    """HBR listesi görünümü"""
    try:
        project_code = request.args.get('project', current_user.get_assigned_projects()[0] if current_user.get_assigned_projects() else 'belgrad')
        
        if not current_user.can_access_project(project_code):
            flash('Bu projeye erişim yetkiniz yok.', 'error')
            return redirect(url_for('dashboard.index'))
        
        # Excel dosyalarını oku
        from routes.fracas import get_excel_path
        excel_path = get_excel_path(project_code, 'HBR')
        
        if not os.path.exists(excel_path):
            flash('HBR dosyası bulunamadı.', 'warning')
            return render_template('hbr/listesi.html', hbr_list=[], project_code=project_code)
        
        # HBR verilerini oku
        import openpyxl
        wb = openpyxl.load_workbook(excel_path)
        ws = wb.active
        
        hbr_list = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:  # HBR ID varsa
                hbr_list.append({
                    'id': row[0],
                    'equipment': row[1],
                    'system': row[2],
                    'status': row[3],
                    'date': row[4]
                })
        
        logger.info(f"HBR listesi yüklendi: {len(hbr_list)} kayıt ({project_code})")
        return render_template('hbr/listesi.html', hbr_list=hbr_list, project_code=project_code)
        
    except Exception as e:
        logger.error(f"HBR listesi hatası: {e}")
        flash(f'Hata: {str(e)}', 'danger')
        return redirect(url_for('dashboard.index'))


@bp.route('/indir')
@login_required
def indir():
    """HBR dosyasını indir"""
    try:
        project_code = request.args.get('project', current_user.get_assigned_projects()[0] if current_user.get_assigned_projects() else 'belgrad')
        
        if not current_user.can_access_project(project_code):
            flash('Bu projeye erişim yetkiniz yok.', 'error')
            return redirect(url_for('dashboard.index'))
        
        from routes.fracas import get_excel_path
        excel_path = get_excel_path(project_code, 'HBR')
        
        if not os.path.exists(excel_path):
            flash('HBR dosyası bulunamadı.', 'warning')
            return redirect(url_for('hbr.listesi'))
        
        logger.info(f"HBR dosyası indirildi: {project_code}")
        
        # Dosya adını belirle
        filename = f'HBR_{project_code}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return send_file(
            excel_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.error(f"HBR indirme hatası: {e}")
        flash(f'Hata: {str(e)}', 'danger')
        return redirect(url_for('hbr.listesi'))


@bp.route('/sil/<filename>', methods=['POST'])
@login_required
def sil(filename: str):
    """HBR dosyasını sil"""
    try:
        if not current_user.is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        project_code = request.form.get('project', 'belgrad')
        
        if not current_user.can_access_project(project_code):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Dosya yolunu oluştur ve sil
        from routes.fracas import get_excel_path
        file_path = get_excel_path(project_code, f'HBR_{filename}')
        
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"HBR dosyası silindi: {filename} ({project_code})")
            return jsonify({'success': True})
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        logger.error(f"HBR silme hatası: {e}")
        return jsonify({'error': str(e)}), 500
