"""
Admin Paneli - Proje Yönetimi, Kullanıcı Yönetimi, Yedekleme
Yalnız admin rolüne sahip kullanıcılar erişebilir
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session, current_app
from flask_login import login_required, current_user
from models import db, User, Role
from utils.project_manager import ProjectManager
from utils.backup_manager import BackupManager
from datetime import datetime
import json
import os

bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Admin yetkisi kontrolü"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Bu sayfaya erişim yetkiniz yok. Admin gerekli.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin Dashboard"""
    # İstatistikler
    total_users = User.query.count()
    admin_users = User.query.filter_by(role='admin').count()
    saha_users = User.query.filter_by(role='saha').count()
    
    # Projeler
    projects = ProjectManager.get_all_projects()
    active_projects = len([p for p in projects if p.get('status') == 'aktif'])
    
    # Son kullanıcı aktiviteleri
    recent_users = User.query.order_by(User.last_login.desc()).limit(5).all()
    
    # Son yedekleme
    projects_list = ProjectManager.get_active_projects()
    backup_info = {}
    for project in projects_list:
        backups = BackupManager.get_backup_history(project['code'])
        if backups:
            backup_info[project['code']] = {
                'last_backup': backups[0]['date'],
                'backup_count': len(backups)
            }
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         admin_users=admin_users,
                         saha_users=saha_users,
                         projects_count=len(projects),
                         active_projects=active_projects,
                         recent_users=recent_users,
                         backup_info=backup_info)


@bp.route('/users')
@login_required
@admin_required
def users():
    """Kullanıcı Yönetimi"""
    users_list = User.query.all()
    all_roles = Role.query.all()  # Dropdown için tüm roller
    return render_template('admin/users.html', users=users_list, all_roles=all_roles)


@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Yeni Kullanıcı Ekle"""
    projects = ProjectManager.get_active_projects()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'saha')  # admin veya saha
        assigned_projects = request.form.getlist('assigned_projects')
        
        # Validasyon
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten var!', 'danger')
            return redirect(url_for('admin.add_user'))
        
        if User.query.filter_by(email=email).first():
            flash('Bu email zaten var!', 'danger')
            return redirect(url_for('admin.add_user'))
        
        # Yeni kullanıcı oluştur
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role
        )
        user.set_password(password)
        
        # Admin ise tüm projelere erişim, saha ise seçilen projeler
        if role == 'admin':
            user.set_assigned_projects(['*'])
        else:
            user.set_assigned_projects(assigned_projects if assigned_projects else [])
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Kullanıcı "{full_name}" başarıyla oluşturuldu!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/add_user.html', projects=projects)


@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Kullanıcı Düzenle"""
    user = User.query.get_or_404(user_id)
    projects = ProjectManager.get_active_projects()
    
    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.email = request.form.get('email')
        user.role = request.form.get('role', 'saha')
        
        # Rol değişirse projeleri güncelle
        assigned_projects = request.form.getlist('assigned_projects')
        if user.role == 'admin':
            user.set_assigned_projects(['*'])
        else:
            user.set_assigned_projects(assigned_projects if assigned_projects else [])
        
        password = request.form.get('password')
        if password:
            user.set_password(password)
        
        db.session.commit()
        flash(f'Kullanıcı "{user.full_name}" başarıyla güncellendi!', 'success')
        return redirect(url_for('admin.users'))
    
    current_projects = user.get_assigned_projects() if user.role == 'saha' else []
    return render_template('admin/edit_user.html', user=user, projects=projects, current_projects=current_projects)


@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Kullanıcı Sil"""
    if user_id == current_user.id:
        flash('Kendi hesabınızı silemezsiniz!', 'danger')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Kullanıcı "{user.full_name}" başarıyla silindi!', 'success')
    return redirect(url_for('admin.users'))


@bp.route('/users/<int:user_id>/change-role', methods=['POST'])
@login_required
@admin_required
def change_user_role(user_id):
    """Kullanıcı Rolünü Değiştir (AJAX)"""
    try:
        if user_id == current_user.id:
            return jsonify({'success': False, 'message': 'Kendi rolünüzü değiştiremezsiniz!'}), 400
        
        user = User.query.get_or_404(user_id)
        
        # JSON data'yı al
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'message': 'Geçersiz istek!'}), 400
        
        # Yeni role_id (integer)
        try:
            new_role_id = int(data.get('role', 0))
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Geçersiz rol!'}), 400
        
        # Rolü veritabanından al
        new_role = Role.query.get(new_role_id)
        if not new_role:
            return jsonify({'success': False, 'message': 'Rol bulunamadı!'}), 400
        
        # Admin sayısını kontrol et (en az 1 admin kalmalı)
        if user.is_admin() and new_role.name != 'admin':
            admin_role = Role.query.filter_by(name='admin').first()
            admin_users = User.query.filter(User.role_id == admin_role.id).count() if admin_role else 0
            if admin_users <= 1:
                return jsonify({'success': False, 'message': "Sistem'de en az 1 admin kalmalıdır!"}), 400
        
        # Rolü değiştir
        old_role_name = user.role_obj.name if user.role_obj else user.role
        user.role_id = new_role_id
        
        # Admin ise tüm projelere, değilse hiç proje yok
        if new_role.name == 'admin':
            user.set_assigned_projects(['*'])
        else:
            user.set_assigned_projects([])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Kullanıcı rolü "{old_role_name}" → "{new_role.name}" değiştirildi',
            'new_role': new_role.name
        }), 200
        
    except Exception as e:
        logger.error(f'[CHANGE_ROLE] Exception: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'}), 500


@bp.route('/projects')
@login_required
@admin_required
def projects():
    """Proje Yönetimi"""
    projects = ProjectManager.get_all_projects()
    
    # Her proje için yapı bilgisi
    project_details = []
    for project in projects:
        structure = ProjectManager.get_project_structure(project['code'])
        project_details.append({
            'project': project,
            'structure': structure
        })
    
    return render_template('admin/projects.html', projects=project_details)


@bp.route('/projects/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_project():
    """Yeni Proje Ekle"""
    if request.method == 'POST':
        code = request.form.get('code', '').lower().strip()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '')
        location = request.form.get('location', '')
        
        # Güvenlik: proje kodu sadece alfanumerik ve tire
        code = ''.join(c for c in code if c.isalnum() or c in ('_', '-'))
        
        if not code or not name:
            flash('Proje kodu ve adı zorunludur', 'danger')
            return render_template('admin/add_project.html')
        
        # Veriler.xlsx dosyası (opsiyonel)
        veriler_file = request.files.get('veriler_file')
        if veriler_file and veriler_file.filename:
            if not veriler_file.filename.endswith('.xlsx'):
                flash('Sadece .xlsx dosyası yüklenebilir', 'danger')
                return render_template('admin/add_project.html')
        else:
            veriler_file = None
        
        success, message = ProjectManager.add_project(code, name, description, location, veriler_file)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('admin.projects'))
        else:
            flash(message, 'danger')
    
    return render_template('admin/add_project.html')


@bp.route('/projects/<project_code>/delete', methods=['POST'])
@login_required
@admin_required
def delete_project(project_code):
    """Proje Sil (Soft Delete = Arşivle)"""
    success, message = ProjectManager.delete_project(project_code, hard_delete=False)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.projects'))


@bp.route('/backups')
@login_required
@admin_required
def backups():
    """Yedekleme Yönetimi"""
    projects = ProjectManager.get_active_projects()
    
    backup_data = {}
    for project in projects:
        backups = BackupManager.get_backup_history(project['code'])
        backup_data[project['code']] = {
            'project_name': project['name'],
            'backups': backups,
            'count': len(backups)
        }
    
    return render_template('admin/backups.html', backup_data=backup_data)


@bp.route('/backups/project/<project_code>', methods=['POST'])
@login_required
@admin_required
def backup_project(project_code):
    """Projeyi Manuel Yedekle"""
    success, message = BackupManager.backup_project_full(project_code)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.backups'))


@bp.route('/backups/all', methods=['POST'])
@login_required
@admin_required
def backup_all():
    """Tüm Projeleri Yedekle"""
    results = BackupManager.backup_all_projects()
    
    success_count = sum(1 for r in results if r['success'])
    flash(f"{success_count}/{len(results)} proje başarıyla yedeklendi!", 'success')
    
    return redirect(url_for('admin.backups'))


@bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """Admin istatistikleri (AJAX)"""
    total_users = User.query.count()
    admin_users = User.query.filter_by(role='admin').count()
    saha_users = User.query.filter_by(role='saha').count()
    
    projects = ProjectManager.get_all_projects()
    active_projects = len([p for p in projects if p.get('status') == 'aktif'])
    
    return jsonify({
        'total_users': total_users,
        'admin_users': admin_users,
        'saha_users': saha_users,
        'total_projects': len(projects),
        'active_projects': active_projects
    })


@bp.route('/yetkilendirme', methods=['GET', 'POST'])
@login_required
@admin_required
def yetkilendirme():
    """Rol ve Yetki Yönetimi Paneli - Rol-İzin Matrisi"""
    from app import PAGES, PROJECTS
    
    roles = Role.query.all()
    users = User.query.all()
    
    # Sayfa izinleri (app.py'deki PAGES listesinden)
    page_perms = [
        {'id': p['id'], 'name': p['code'], 'description': p['name'], 'category': 'page', 'section': p['section']}
        for p in PAGES
    ]
    
    # Proje izinleri (app.py'deki PROJECTS listesinden)
    project_perms = [
        {'id': 100 + i, 'name': p['code'], 'description': p['name'], 'category': 'project'}
        for i, p in enumerate(PROJECTS)
    ]
    
    all_permissions = page_perms + project_perms
    
    # Her role'un izinlerini dict olarak hazırla
    role_permissions_map = {}
    for role in roles:
        perms = role.get_permissions()
        role_permissions_map[role.id] = perms
    
    return render_template('admin/permissions.html', 
                         roles=roles,
                         users=users,
                         all_permissions=all_permissions,
                         page_perms=page_perms,
                         project_perms=project_perms,
                         role_permissions_map=role_permissions_map)


# ── Geçmiş Veri Yükleme (RCA için) ──────────────────────────────
@bp.route('/import-data')
@login_required
@admin_required
def import_data_page():
    """Geçmiş veri yükleme sayfası"""
    projects = ProjectManager.get_active_projects()
    return render_template('admin/import_data.html', projects=projects)


@bp.route('/api/sync-excel-to-db', methods=['POST'])
@login_required
@admin_required
def sync_excel_to_db():
    """Mevcut Servis_Durumu.xlsx verilerini DB'ye aktar (tüm projeler veya tek proje)"""
    from utils.utils_project_excel_store import import_servis_durumu_grid_to_db
    
    project_code = request.json.get('project_code', 'all')
    
    if project_code == 'all':
        projects = ProjectManager.get_active_projects()
        results = {}
        for p in projects:
            code = p.get('code', p.get('name', ''))
            try:
                result = import_servis_durumu_grid_to_db(code)
                results[code] = result
            except Exception as e:
                results[code] = {'error': str(e)}
        
        total_inserted = sum(r.get('inserted', 0) for r in results.values())
        total_updated = sum(r.get('updated', 0) for r in results.values())
        return jsonify({
            'success': True,
            'message': f'Tüm projeler senkronize edildi: {total_inserted} yeni, {total_updated} güncellenen kayıt',
            'details': results
        })
    else:
        try:
            result = import_servis_durumu_grid_to_db(project_code)
            return jsonify({
                'success': True,
                'message': f'{project_code}: {result.get("inserted", 0)} yeni, {result.get("updated", 0)} güncellenen kayıt',
                'details': result
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/upload-historical', methods=['POST'])
@login_required
@admin_required
def upload_historical_data():
    """Harici Excel dosyasından geçmiş veri yükle"""
    from utils.utils_project_excel_store import import_historical_excel_to_system
    import tempfile
    
    project_code = request.form.get('project_code')
    if not project_code:
        return jsonify({'success': False, 'message': 'Proje kodu gerekli'}), 400
    
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({'success': False, 'message': 'Excel dosyası gerekli'}), 400
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'success': False, 'message': 'Sadece .xlsx dosyaları desteklenir'}), 400
    
    # Güvenli geçici dosya oluştur
    tmp_dir = os.path.join(current_app.root_path, 'data', 'uploads')
    os.makedirs(tmp_dir, exist_ok=True)
    
    # Güvenli dosya adı
    from werkzeug.utils import secure_filename
    safe_name = secure_filename(file.filename)
    tmp_path = os.path.join(tmp_dir, f'import_{project_code}_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{safe_name}')
    
    try:
        file.save(tmp_path)
        result = import_historical_excel_to_system(project_code, tmp_path)
        
        if result.get('error'):
            return jsonify({'success': False, 'message': result['error']}), 400
        
        return jsonify({
            'success': True,
            'message': f'{project_code}: {result["db_inserted"]} yeni, {result["db_updated"]} güncellenen DB kaydı, {result["excel_written"]} Excel hücresi yazıldı',
            'details': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        # Geçici dosyayı temizle
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@bp.route('/api/db-status')
@login_required
@admin_required
def db_data_status():
    """Projelerin DB'deki veri durumunu göster"""
    from models import ServiceStatus
    from sqlalchemy import func
    
    projects = ProjectManager.get_active_projects()
    status = {}
    
    for p in projects:
        code = p.get('code', p.get('name', ''))
        total = ServiceStatus.query.filter_by(project_code=code).count()
        disi = ServiceStatus.query.filter(
            ServiceStatus.project_code == code,
            ServiceStatus.status.in_(['Servis Dışı', 'İşletme Kaynaklı Servis Dışı', 'Servis Disi'])
        ).count()
        with_sistem = ServiceStatus.query.filter(
            ServiceStatus.project_code == code,
            ServiceStatus.sistem != None,
            ServiceStatus.sistem != ''
        ).count()
        
        date_range = db.session.query(
            func.min(ServiceStatus.date),
            func.max(ServiceStatus.date)
        ).filter_by(project_code=code).first()
        
        status[code] = {
            'total': total,
            'servis_disi': disi,
            'with_sistem': with_sistem,
            'date_min': str(date_range[0]) if date_range and date_range[0] else '-',
            'date_max': str(date_range[1]) if date_range and date_range[1] else '-'
        }
    
    return jsonify({'success': True, 'status': status})
