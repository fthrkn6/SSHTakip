"""
Admin Paneli - Rol Yönetimi
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, User, Role
from functools import wraps

bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Admin yetkisi kontrolü"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Bu sayfaya erişim yetkiniz yok. Admin gerekli.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/permissions')
@login_required
@admin_required
def permissions():
    """Rol ve Yetki Yönetimi Paneli"""
    roles = Role.query.all()
    users = User.query.all()
    return render_template('admin/permissions.html', roles=roles, users=users)


@bp.route('/add_role', methods=['POST'])
@login_required
@admin_required
def add_role():
    """Yeni Rol Ekle"""
    name = request.form.get('name')
    description = request.form.get('description')
    
    if not name:
        flash('Rol adı gerekli!', 'danger')
        return redirect(url_for('admin.permissions'))
    
    if Role.query.filter_by(name=name).first():
        flash('Bu rol zaten mevcut!', 'danger')
        return redirect(url_for('admin.permissions'))
    
    role = Role(name=name, description=description)
    db.session.add(role)
    db.session.commit()
    
    flash('Rol başarıyla eklendi!', 'success')
    return redirect(url_for('admin.permissions'))


@bp.route('/edit_role', methods=['POST'])
@login_required
@admin_required
def edit_role():
    """Rol Düzenle"""
    role_id = request.form.get('id')
    name = request.form.get('name')
    description = request.form.get('description')
    
    role = Role.query.get(role_id)
    if not role:
        flash('Rol bulunamadı!', 'danger')
        return redirect(url_for('admin.permissions'))
    
    role.name = name
    role.description = description
    db.session.commit()
    
    flash('Rol güncellendi!', 'success')
    return redirect(url_for('admin.permissions'))


@bp.route('/delete_role', methods=['POST'])
@login_required
@admin_required
def delete_role():
    """Rol Sil"""
    role_id = request.form.get('id')
    role = Role.query.get(role_id)
    
    if not role:
        flash('Rol bulunamadı!', 'danger')
        return redirect(url_for('admin.permissions'))
    
    if role.users:
        flash('Bu role atanmış kullanıcılar var, önce kullanıcıların rolünü değiştirin!', 'danger')
        return redirect(url_for('admin.permissions'))
    
    db.session.delete(role)
    db.session.commit()
    
    flash('Rol silindi!', 'success')
    return redirect(url_for('admin.permissions'))
