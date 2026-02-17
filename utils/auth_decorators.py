"""
Rol Tabanlı Erişim Kontrol Dekoratörleri
admin / saha / proje erişim kontrolleri
"""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def require_admin(f):
    """
    Sadece admin rolüne sahip kullanıcıların erişmesine izin ver.
    
    Kullanım:
        @bp.route('/admin/dashboard')
        @login_required
        @require_admin
        def admin_dashboard():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Lütfen giriş yapın.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin():
            flash('Bu sayfaya erişim yetkiniz yok. Admin gerekli.', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def require_project_access(project_code_param='project_code'):
    """
    Kullanıcının belirli bir projeye erişimini kontrol et.
    
    Kullanım:
        @bp.route('/project/<project_code>/dashboard')
        @login_required
        @require_project_access('project_code')
        def project_dashboard(project_code):
            ...
    
    Parameters:
        project_code_param: Route parameter adı (default: 'project_code')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Lütfen giriş yapın.', 'warning')
                return redirect(url_for('auth.login'))
            
            project_code = kwargs.get(project_code_param)
            
            if not project_code:
                flash('Proje belirtilmedi.', 'danger')
                return redirect(url_for('dashboard.index'))
            
            if not current_user.can_access_project(project_code):
                flash(f'"{project_code}" projesine erişim yetkiniz yok.', 'danger')
                return redirect(url_for('dashboard.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_saha_role(f):
    """
    Sadece saha rolüne sahip kullanıcıların erişmesine izin ver.
    
    Kullanım:
        @bp.route('/field/equipment')
        @login_required
        @require_saha_role
        def field_equipment():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Lütfen giriş yapın.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_saha():
            flash('Bu sayfa yalnız saha kullanıcıları için açıktır.', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def check_project_in_session():
    """
    Session'daki project_code'un, kullanıcı tarafından erişilebilir olduğunu kontrol et.
    
    Kullanım:
        @bp.before_request
        def before_request():
            check_project_in_session()
    """
    from flask import session
    
    if 'project_code' in session:
        project_code = session['project_code']
        if not current_user.can_access_project(project_code):
            # Erişim yetki yok, varsayılan projeye döndür
            available_projects = current_user.get_assigned_projects()
            if available_projects and available_projects != '*':
                session['project_code'] = available_projects[0]
            else:
                session['project_code'] = 'belgrad'  # Default fallback
