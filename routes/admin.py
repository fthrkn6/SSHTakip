"""
Admin Paneli - Proje Yönetimi, Kullanıcı Yönetimi, Yedekleme
Yalnız admin rolüne sahip kullanıcılar erişebilir
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session, current_app
from flask_login import login_required, current_user
from models import db, User
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
    return render_template('admin/users.html', users=users_list)


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
        code = request.form.get('code').lower().strip()
        name = request.form.get('name')
        description = request.form.get('description', '')
        location = request.form.get('location', '')
        
        success, message = ProjectManager.add_project(code, name, description, location)
        
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
    """Sayfa izinlerini yönet - Role-based authorization"""
    from models import Permission, RolePermission
    
    if request.method == 'POST':
        # POST isteği: İzinleri güncelle
        role = request.form.get('role')
        selected_perm_ids = request.form.getlist('permissions')
        
        if not role:
            flash('Rol gerekli.', 'danger')
            return redirect(url_for('admin.yetkilendirme'))
        
        # Permission ID'lerini page_name'e çevir
        selected_page_names = []
        for perm_id in selected_perm_ids:
            perm = Permission.query.get(perm_id)
            if perm:
                selected_page_names.append(perm.page_name)
        
        # Mevcut izinleri sil (role + page_name)
        cursor = db.session.connection().connection.cursor()
        cursor.execute("DELETE FROM role_permission WHERE role = ?", (role,))
        db.session.connection().connection.commit()
        
        # Yeni izinleri ekle
        for page_name in selected_page_names:
            cursor.execute(
                "INSERT INTO role_permission (role, page_name, can_view, can_edit, can_delete) VALUES (?, ?, ?, ?, ?)",
                (role, page_name, 1, 1, 0)
            )
        
        db.session.connection().connection.commit()
        flash(f'"{role}" rolü izinleri güncellendi.', 'success')
        return redirect(url_for('admin.yetkilendirme'))
    
    # GET isteği: Form göster
    users = User.query.all()
    permissions = Permission.query.all()
    
    # Her rol için izinleri yükle - role_permission tablosundan page_name'i al
    role_permissions = {}
    for role in ['admin', 'manager', 'saha']:
        # Database schema'sında page_name var
        cursor = db.session.connection().connection.cursor()
        cursor.execute(
            "SELECT DISTINCT page_name FROM role_permission WHERE role = ?",
            (role,)
        )
        role_permissions[role] = [row[0] for row in cursor.fetchall()]
    
    # Rol sayılarını hesapla
    role_counts = {
        'admin': User.query.filter_by(role='admin').count(),
        'manager': User.query.filter_by(role='manager').count(),
        'saha': User.query.filter_by(role='saha').count(),
    }
    
    return render_template(
        'admin/permissions.html',
        users=users,
        permissions=permissions,
        role_permissions=role_permissions,
        role_counts=role_counts
    )
