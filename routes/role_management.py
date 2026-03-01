"""
Rol Yönetimi - Admin Routes
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Role, User
from functools import wraps

bp_roles = Blueprint('role_mgmt', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Yetkiniz yok!', 'danger')
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

@bp_roles.route('/permissions')
@login_required
@admin_required
def permissions():
    """ESKİ ROUTE - Yeni /admin/yetkilendirme'e redirect et"""
    from flask import redirect, url_for
    return redirect(url_for('admin.yetkilendirme'))

@bp_roles.route('/permissions/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_permission():
    """Rol-İzin ilişkisini aç/kapat"""
    try:
        data = request.get_json()
        role_id = data.get('role_id')
        permission_id = data.get('permission_id')
        
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'success': False, 'message': 'Rol bulunamadı!'}), 404
        
        # Role'un mevcut izinlerini al (JSON'dan)
        perms = role.get_permissions()
        
        # permission_id'yi string'e çevir (JSON'da key)
        perm_key = f'perm_{permission_id}'
        
        # İzni toggle et
        if perm_key in perms:
            del perms[perm_key]
            action = 'Kaldırıldı'
        else:
            perms[perm_key] = True
            action = 'Eklendi'
        
        # Güncellenen izinleri kaydet
        role.set_permissions(perms)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'{action}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp_roles.route('/add_role', methods=['POST'])
@login_required
@admin_required
def add_role():
    name = request.form.get('name')
    description = request.form.get('description')
    if not name:
        flash('Rol adı gerekli!', 'danger')
        return redirect(url_for('role_mgmt.permissions'))
    if Role.query.filter_by(name=name).first():
        flash('Bu rol zaten var!', 'danger')
        return redirect(url_for('role_mgmt.permissions'))
    role = Role(name=name, description=description)
    db.session.add(role)
    db.session.commit()
    flash('Rol eklendi!', 'success')
    return redirect(url_for('role_mgmt.permissions'))

@bp_roles.route('/edit_role', methods=['POST'])
@login_required
@admin_required
def edit_role():
    role_id = request.form.get('id')
    name = request.form.get('name')
    description = request.form.get('description')
    role = Role.query.get(role_id)
    if not role:
        flash('Rol bulunamadı!', 'danger')
        return redirect(url_for('role_mgmt.permissions'))
    role.name = name
    role.description = description
    db.session.commit()
    flash('Rol güncellendi!', 'success')
    return redirect(url_for('role_mgmt.permissions'))

@bp_roles.route('/delete_role', methods=['POST'])
@login_required
@admin_required
def delete_role():
    role_id = request.form.get('id')
    role = Role.query.get(role_id)
    if not role:
        flash('Rol bulunamadı!', 'danger')
        return redirect(url_for('role_mgmt.permissions'))
    if role.users:
        flash('Bu role kullanıcı atanmış!', 'danger')
        return redirect(url_for('role_mgmt.permissions'))
    db.session.delete(role)
    db.session.commit()
    flash('Rol silindi!', 'success')
    return redirect(url_for('role_mgmt.permissions'))

@bp_roles.route('/users/<int:user_id>/update-role', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    """Kullanıcının rolünü güncelle"""
    user = User.query.get(user_id)
    if not user:
        flash('Kullanıcı bulunamadı!', 'danger')
        return redirect(url_for('role_mgmt.permissions'))
    
    role_id = request.form.get('role_id')
    if not role_id:
        flash('Rol seçiniz!', 'danger')
        return redirect(url_for('role_mgmt.permissions'))
    
    role = Role.query.get(role_id)
    if not role:
        flash('Rol bulunamadı!', 'danger')
        return redirect(url_for('role_mgmt.permissions'))
    
    # User'ın role_id'sini güncelle
    user.role_id = role.id
    user.role = role.name  # Backward compatibility için
    db.session.commit()
    
    flash(f'{user.full_name} kullanıcısının rolü {role.name} olarak güncellendi!', 'success')
    return redirect(url_for('role_mgmt.permissions'))
