from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Kullanıcı girişi - ISO 27001 uyumlu"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Hesabınız devre dışı bırakılmış.', 'error')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Geçersiz kullanıcı adı veya şifre.', 'error')
    
    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    """Kullanıcı çıkışı"""
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Yeni kullanıcı kaydı - Sadece admin yapabilir"""
    if current_user.role != 'admin':
        flash('Bu işlem için yetkiniz yok.', 'error')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'technician')
        department = request.form.get('department')
        phone = request.form.get('phone')
        
        # Kullanıcı var mı kontrol et
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor.', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Bu e-posta adresi zaten kullanılıyor.', 'error')
            return redirect(url_for('auth.register'))
        
        # Yeni kullanıcı oluştur
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            department=department,
            phone=phone
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'{username} kullanıcısı başarıyla oluşturuldu.', 'success')
        return redirect(url_for('auth.users'))
    
    return render_template('auth/register.html')


@bp.route('/users')
@login_required
def users():
    """Kullanıcı listesi"""
    if current_user.role not in ['admin', 'manager']:
        flash('Bu sayfaya erişim yetkiniz yok.', 'error')
        return redirect(url_for('dashboard.index'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('auth/users.html', users=users)


@bp.route('/profile')
@login_required
def profile():
    """Kullanıcı profili"""
    return render_template('auth/profile.html')


@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Şifre değiştirme"""
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_user.check_password(old_password):
        flash('Mevcut şifre yanlış.', 'error')
        return redirect(url_for('auth.profile'))
    
    if new_password != confirm_password:
        flash('Yeni şifreler eşleşmiyor.', 'error')
        return redirect(url_for('auth.profile'))
    
    current_user.set_password(new_password)
    db.session.commit()
    
    flash('Şifreniz başarıyla değiştirildi.', 'success')
    return redirect(url_for('auth.profile'))
