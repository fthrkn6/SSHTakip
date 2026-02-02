from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Equipment, Failure
from datetime import datetime

bp = Blueprint('failure', __name__, url_prefix='/arizalar')


@bp.route('/')
@login_required
def list():
    """Arıza listesi"""
    
    status_filter = request.args.get('status', 'all')
    arac_filter = request.args.get('arac', 'all')
    
    query = Failure.query
    
    if status_filter == 'active':
        query = query.filter_by(resolved=False)
    elif status_filter == 'resolved':
        query = query.filter_by(resolved=True)
    
    if arac_filter != 'all':
        query = query.filter_by(equipment_id=arac_filter)
    
    arizalar = query.order_by(Failure.failure_date.desc()).all()
    
    # Araçları al (dropdown için)
    araclar = Equipment.query.filter_by(equipment_type='arac').all()
    
    # İstatistikler
    stats = {
        'total': Failure.query.count(),
        'active': Failure.query.filter_by(resolved=False).count(),
        'resolved': Failure.query.filter_by(resolved=True).count(),
        'critical': Failure.query.filter_by(severity='critical', resolved=False).count()
    }
    
    return render_template('failure/list.html',
                          arizalar=arizalar,
                          araclar=araclar,
                          stats=stats,
                          filters={'status': status_filter, 'arac': arac_filter})


@bp.route('/ekle', methods=['GET', 'POST'])
@login_required
def add():
    """Yeni arıza kaydı"""
    
    if request.method == 'POST':
        ariza = Failure(
            failure_code=f"ARZ-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            equipment_id=request.form.get('arac_id'),
            failure_date=datetime.strptime(request.form.get('failure_date'), '%Y-%m-%dT%H:%M'),
            description=request.form.get('description'),
            severity=request.form.get('severity'),
            failure_type=request.form.get('failure_type'),
            reported_by=current_user.id,
            resolved=False
        )
        
        # Aracın durumunu arızalı yap
        arac = Equipment.query.get(request.form.get('arac_id'))
        if arac:
            arac.status = 'ariza'
        
        db.session.add(ariza)
        db.session.commit()
        
        flash('Arıza kaydı başarıyla oluşturuldu.', 'success')
        return redirect(url_for('failure.list'))
    
    araclar = Equipment.query.filter_by(equipment_type='arac').all()
    
    ariza_turleri = [
        ('mekanik', 'Mekanik Arıza'),
        ('elektrik', 'Elektrik Arızası'),
        ('elektronik', 'Elektronik Arıza'),
        ('hidrolik', 'Hidrolik Arıza'),
        ('pnomatik', 'Pnömatik Arıza'),
        ('yapi', 'Yapısal Hasar'),
        ('diger', 'Diğer')
    ]
    
    return render_template('failure/add.html', 
                          araclar=araclar,
                          ariza_turleri=ariza_turleri)


@bp.route('/<int:id>')
@login_required
def detail(id):
    """Arıza detayı"""
    ariza = Failure.query.get_or_404(id)
    return render_template('failure/detail.html', ariza=ariza)


@bp.route('/<int:id>/cozuldu', methods=['POST'])
@login_required
def resolve(id):
    """Arızayı çözüldü olarak işaretle"""
    
    ariza = Failure.query.get_or_404(id)
    ariza.resolved = True
    ariza.resolution_date = datetime.utcnow()
    ariza.resolution_notes = request.form.get('resolution_notes')
    ariza.resolved_by = current_user.id
    
    # Araç durumunu güncelle (başka aktif arızası yoksa)
    arac = Equipment.query.get(ariza.equipment_id)
    diger_arizalar = Failure.query.filter_by(
        equipment_id=ariza.equipment_id, 
        resolved=False
    ).filter(Failure.id != id).count()
    
    if diger_arizalar == 0 and arac:
        arac.status = 'servis'
    
    db.session.commit()
    flash('Arıza çözüldü olarak işaretlendi.', 'success')
    
    return redirect(url_for('failure.detail', id=id))