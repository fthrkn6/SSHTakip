from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_required, current_user
from models import db, Equipment, Failure
from datetime import datetime
from utils_hbr_manager import HBRManager
import os
from werkzeug.utils import secure_filename

bp = Blueprint('failure', __name__, url_prefix='/arizalar')


@bp.route('/')
@login_required
def list():
    """Arıza listesi"""
    current_project = session.get('current_project', 'belgrad')
    status_filter = request.args.get('status', 'all')
    arac_filter = request.args.get('arac', 'all')
    
    query = Failure.query.filter_by(project_code=current_project)
    
    if status_filter == 'active':
        query = query.filter_by(resolved=False)
    elif status_filter == 'resolved':
        query = query.filter_by(resolved=True)
    
    if arac_filter != 'all':
        query = query.filter_by(equipment_id=arac_filter)
    
    arizalar = query.order_by(Failure.failure_date.desc()).all()
    
    # Araçları al (dropdown için)
    araclar = Equipment.query.filter_by(equipment_type='arac', project_code=current_project).all()
    
    # HBR listesini yükle
    hbr_files = _load_hbr_files(current_project)
    
    # İstatistikler
    stats = {
        'total': Failure.query.filter_by(project_code=current_project).count(),
        'active': Failure.query.filter_by(project_code=current_project, resolved=False).count(),
        'resolved': Failure.query.filter_by(project_code=current_project, resolved=True).count(),
        'critical': Failure.query.filter_by(project_code=current_project, severity='critical', resolved=False).count(),
        'hbr_total': len(hbr_files)
    }
    
    return render_template('failure/list.html',
                          arizalar=arizalar,
                          hbr_files=hbr_files,
                          araclar=araclar,
                          stats=stats,
                          filters={'status': status_filter, 'arac': arac_filter})


@bp.route('/ekle', methods=['GET', 'POST'])
@login_required
def add():
    """Yeni arıza kaydı - HBR desteği ile"""
    
    if request.method == 'POST':
        # Arıza kaydı oluştur
        failure_date_str = request.form.get('ariza_tarihi')
        if failure_date_str:
            failure_date = datetime.strptime(failure_date_str, '%Y-%m-%dT%H:%M')
        else:
            failure_date = datetime.now()
            
        ariza = Failure(
            failure_code=f"ARZ-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            equipment_id=request.form.get('arac_id'),
            failure_date=failure_date,
            description=request.form.get('description'),
            severity=request.form.get('severity'),
            failure_type=request.form.get('failure_type'),
            reported_by=current_user.id,
            resolved=False
        )
        
        # Aracın durumunu arızalı yap - project_code ile filtrele
        current_project = session.get('current_project', 'belgrad')
        arac = Equipment.query.filter_by(id=request.form.get('arac_id'), project_code=current_project).first()
        if arac:
            arac.status = 'ariza'
        
        db.session.add(ariza)
        db.session.flush()  # ID'yi al
        
        # HBR oluştur (checkbox işaretliyse)
        if request.form.get('create_hbr') == 'true':
            hbr_success = _create_hbr_from_form(ariza, request)
            if hbr_success:
                flash('Arıza HBR dosyası başarıyla oluşturuldu.', 'info')
            else:
                flash('Arıza kaydı oluşturuldu ama HBR dosyası oluşturulamadı.', 'warning')
        
        db.session.commit()
        
        flash('Arıza kaydı başarıyla oluşturuldu.', 'success')
        return redirect(url_for('failure.list'))
    
    # Mevcut projede araçları göster
    current_project = session.get('current_project', 'belgrad')
    araclar = Equipment.query.filter_by(equipment_type='arac', project_code=current_project).all()
    
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
                          ariza_turleri=ariza_turleri,
                          now=datetime.now())


@bp.route('/<int:id>')
@login_required
def detail(id):
    """Arıza detayı"""
    current_project = session.get('current_project', 'belgrad')
    ariza = Failure.query.filter_by(
        id=id,
        project_code=current_project
    ).first_or_404()
    return render_template('failure/detail.html', ariza=ariza)


def _create_hbr_from_form(ariza, request):
    """Form verilerinden HBR Excel dosyası oluştur"""
    try:
        from flask import session
        from utils.project_manager import ProjectManager
        from utils_hbr_numbering import get_project_code_from_veriler
        
        # Proje ADI al (session'dan)
        project_name = session.get('current_project', 'belgrad')
        
        # Veriler.xlsx'ten proje KODU al (BEL25, GDM7, etc)
        project_code = get_project_code_from_veriler(project_name)
        logger.info(f"[HBR] Proje: {project_name} → Kod: {project_code}")
        
        # Fotoğraf dosyasını bağlantı yapılan uploads klasöründe kaydet
        fotograf_path = None
        if 'fotograf' in request.files:
            file = request.files['fotograf']
            if file and file.filename:
                # uploads klasörü oluştur
                uploads_dir = os.path.join(current_app.root_path, 'uploads', project_name, 'hbr_fotos')
                os.makedirs(uploads_dir, exist_ok=True)
                
                # Dosya adını safe hale getir
                filename = secure_filename(f"{ariza.failure_code}_{file.filename}")
                fotograf_path = os.path.join(uploads_dir, filename)
                file.save(fotograf_path)
        
        # HBR form verilerini hazırla
        hbr_data = {
            'malzeme_no': request.form.get('malzeme_no', ''),
            'malzeme_adi': request.form.get('malzeme_adi', ''),
            'ariza_tarihi': ariza.failure_date,
            'ariza_km': request.form.get('ariza_km', ''),
            'tedarikci': request.form.get('tedarikci', ''),
            'musteri': request.form.get('musteri', project_code.upper()),  # Proje kodu kullan
            'tespit_yontemi': request.form.get('tespit_yontemi', ''),
            'musteri_bildirimi': request.form.get('musteri_bildirimi') == 'true',
            'ariza_sinifi': request.form.get('ariza_sinifi', ''),
            'ariza_tipi': request.form.get('ariza_tipi', ''),
            'ariza_tanimi': request.form.get('description', ''),
            'arac_modulu': request.form.get('arac_modulu', ''),
            'parca_seri_no': request.form.get('parca_seri_no', ''),
            'fotograf': fotograf_path,
            'ncr_no': ''  # Sistem tarafından oluşturulacak
        }
        
        # NCR sayıcısını al (project_name ile)
        project_code, counter = HBRManager.get_next_ncr_counter(project_name, current_app.root_path)
        
        # HBR dosyası oluştur
        hbr_file = HBRManager.create_hbr_file(
            project_name,           # Proje ADI (belgrad, iasi, etc)
            current_app.root_path,
            current_user,
            hbr_data,
            project_code=project_code,  # Veriler.xlsx'ten okunan KOD
            counter=counter
        )
        
        return hbr_file is not None
        
    except Exception as e:
        print(f"HBR oluşturma hatası: {e}")
        return False


def _load_hbr_files(project_name):
    """
    HBR dosyalarının listesini yükle
    
    Args:
        project_name: Proje adı (belgrad, iasi, etc)
    """
    import re
    from utils_hbr_numbering import get_project_code_from_veriler
    
    # Veriler.xlsx'ten proje kodu al
    try:
        project_code = get_project_code_from_veriler(project_name)
    except:
        project_code = project_name.upper()[:3] + "25"  # Fallback
    
    hbr_dir = os.path.join(current_app.root_path, 'logs', project_name, 'HBR')
    hbr_files = []
    
    if not os.path.exists(hbr_dir):
        return hbr_files
    
    try:
        # Proje kodunu pattern'e dönüştür
        pattern = re.compile(rf'^{re.escape(project_code)}-NCR-\d+', re.IGNORECASE)
        
        for file in os.listdir(hbr_dir):
            # Proje kodunun dosya adı formatını kontrol et
            if file.endswith('.xlsx') and pattern.match(file):
                file_path = os.path.join(hbr_dir, file)
                file_stat = os.stat(file_path)
                hbr_files.append({
                    'name': file,
                    'path': file_path,
                    'size': file_stat.st_size,
                    'date': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Tarihe göre sırala (en yeni önce)
        hbr_files.sort(key=lambda x: x['date'], reverse=True)
        logger.info(f"[HBR] Yüklendi: {len(hbr_files)} dosya (Proje: {project_name} → {project_code})")
        
    except Exception as e:
        logger.error(f"HBR dosyaları yükleme hatası: {e}")
    
    return hbr_files


@bp.route('/<int:id>/cozuldu', methods=['POST'])
@login_required
def resolve(id):
    """Arızayı çözüldü olarak işaretle"""
    current_project = session.get('current_project', 'belgrad')
    
    ariza = Failure.query.filter_by(
        id=id,
        project_code=current_project
    ).first_or_404()
    ariza.resolved = True
    ariza.resolution_date = datetime.utcnow()
    ariza.resolution_notes = request.form.get('resolution_notes')
    ariza.resolved_by = current_user.id
    
    # Araç durumunu güncelle (başka aktif arızası yoksa)
    arac = Equipment.query.get(ariza.equipment_id)
    diger_arizalar = Failure.query.filter_by(
        equipment_id=ariza.equipment_id, 
        resolved=False,
        project_code=current_project
    ).filter(Failure.id != id).count()
    
    if diger_arizalar == 0 and arac:
        arac.status = 'servis'
    
    db.session.commit()
    flash('Arıza çözüldü olarak işaretlendi.', 'success')
    
    return redirect(url_for('failure.detail', id=id))