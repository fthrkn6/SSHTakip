"""
SSH Takip - Bilgisayarlı Bakım Yönetim Sistemi
Bozankaya Hafif Raylı Sistem için Kapsamlı Bakım Yönetimi
EN 13306, ISO 55000, EN 15341, ISO 27001 Standartlarına Uygun
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from models import db, User, Equipment, Failure, WorkOrder, MaintenancePlan, SparePartInventory, ServiceStatus
from werkzeug.utils import secure_filename
from routes.fracas import bp as fracas_bp, get_excel_path, get_column
from routes.kpi import bp as kpi_bp
from routes.service_status import bp as service_status_bp
import os


ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'dwg', 'jpg', 'png', 'jpeg'}

# Projeler listesi
PROJECTS = [
    {'code': 'belgrad', 'name': 'Belgrad', 'country': 'Sırbistan', 'flag': '🇷🇸'},
    {'code': 'iasi', 'name': 'Iași', 'country': 'Romanya', 'flag': '🇷🇴'},
    {'code': 'timisoara', 'name': 'Timișoara', 'country': 'Romanya', 'flag': '🇹🇷'},
    {'code': 'kayseri', 'name': 'Kayseri', 'country': 'Türkiye', 'flag': '🇹🇷'},
    {'code': 'kocaeli', 'name': 'Kocaeli', 'country': 'Türkiye', 'flag': '🇹🇷'},
    {'code': 'gebze', 'name': 'Gebze', 'country': 'Türkiye', 'flag': '🇹🇷'},
]


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_app():
    print('create_app started')
    try:
        app = Flask(__name__, static_folder='static', static_url_path='/static')
        
        # Configuration
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'bozankaya-ssh_takip-2024-gizli')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ssh_takip_bozankaya.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
        app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

        # Initialize database
        db.init_app(app)

        # Initialize LoginManager
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'login'
        login_manager.login_message = 'Please log in to view this page.'
        login_manager.login_message_category = 'warning'

        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(User, int(user_id))

        # Register blueprints
        app.register_blueprint(fracas_bp)
        app.register_blueprint(kpi_bp)
        app.register_blueprint(service_status_bp)

        # ==================== ROUTES ====================

        @app.route('/')
        def index():
            if current_user.is_authenticated:
                return redirect(url_for('dashboard'))
            return redirect(url_for('login'))

        @app.route('/login', methods=['GET', 'POST'])
        def login():
            if current_user.is_authenticated:
                return redirect(url_for('dashboard'))
            
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                
                user = User.query.filter_by(username=username).first()
                
                if user and user.check_password(password):
                    login_user(user, remember=request.form.get('remember'))
                    user.last_login = datetime.now()
                    db.session.commit()
                    
                    # Set default project if not set
                    if 'current_project' not in session:
                        session['current_project'] = 'belgrad'
                        session['project_code'] = 'belgrad'
                        session['project_name'] = '🇷🇸 Belgrad'
                    
                    next_page = request.args.get('next')
                    if next_page and next_page.startswith('/'):
                        return redirect(next_page)
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid username or password', 'danger')
            
            return render_template('login.html')

        @app.route('/logout')
        @login_required
        def logout():
            logout_user()
            flash('You have been logged out.', 'success')
            return redirect(url_for('login'))

        @app.route('/dashboard')
        @login_required
        def dashboard():
            """Main dashboard"""
            from datetime import datetime
            
            # Ensure project is selected
            if 'current_project' not in session:
                session['current_project'] = 'belgrad'
                session['project_code'] = 'belgrad'
                session['project_name'] = '🇷🇸 Belgrad'
            
            # ServiceStatus'ten Bugünün durumunu çek
            today = datetime.now().strftime('%Y-%m-%d')
            today_service_status = ServiceStatus.query.filter_by(date=today).all()
            
            # Status'a göre sayımlar
            aktif_tramvay = len([s for s in today_service_status if s.status and 'Servis' in s.status and 'Dışı' not in s.status])
            arizali_tramvay = len([s for s in today_service_status if s.status and 'Dışı' in s.status])
            bakimda_tramvay = 0  # ServiceStatus'ta bakım durumu ayrı değil
            
            # Tüm tramvaylar (Excel'den)
            import pandas as pd
            import os
            current_project = session.get('current_project', 'belgrad')
            veriler_path = os.path.join(app.root_path, 'data', current_project, 'Veriler.xlsx')
            toplam_tramvay = 0
            
            if os.path.exists(veriler_path):
                try:
                    df = pd.read_excel(veriler_path, sheet_name=1, header=0, engine='openpyxl')
                    if 'tram_id' in df.columns:
                        toplam_tramvay = len(df['tram_id'].dropna())
                except Exception as e:
                    print(f"Excel okuma hatası: {e}")
            
            # Fleet availability oranı = aktif tramvay / toplam tramvay * 100
            fleet_availability = (aktif_tramvay / toplam_tramvay * 100) if toplam_tramvay > 0 else 0
            
            stats = {
                'total_equipment': Equipment.query.count(),
                'total_failures': Failure.query.count(),
                'total_workorders': WorkOrder.query.count(),
                'total_maintenance_plans': MaintenancePlan.query.count(),
                'total_tramvay': toplam_tramvay,
                'aktif_servis': aktif_tramvay,
                'bakimda': bakimda_tramvay,
                'arizali': arizali_tramvay,
                'aktif_ariza': Failure.query.filter(Failure.status.ilike('open')).count() if Failure.query.count() > 0 else 0,
                'bekleyen_is_emri': WorkOrder.query.filter(WorkOrder.status.ilike('pending')).count() if WorkOrder.query.count() > 0 else 0,
                'devam_eden_is_emri': WorkOrder.query.filter(WorkOrder.status.ilike('in_progress')).count() if WorkOrder.query.count() > 0 else 0,
                'bugun_tamamlanan': WorkOrder.query.filter(WorkOrder.status.ilike('completed')).count() if WorkOrder.query.count() > 0 else 0,
            }
            
            # Get equipment (tramvaylar) - Veriler.xlsx'ten Sayfa2'den tram_id sütununu oku
            import pandas as pd
            import os
            
            current_project = session.get('current_project', 'belgrad')
            veriler_path = os.path.join(app.root_path, 'data', current_project, 'Veriler.xlsx')
            tramvaylar = []
            
            if os.path.exists(veriler_path):
                try:
                    # Sayfa2 (index 1) oku
                    df = pd.read_excel(veriler_path, sheet_name=1, header=0, engine='openpyxl')
                    if 'tram_id' in df.columns:
                        # Excel'den tram_id'leri al
                        tram_ids = df['tram_id'].dropna().astype(str).tolist()
                        
                        # Her tram_id için database'den equipment bilgisini çek
                        for tram_id in tram_ids:
                            tram_id_clean = tram_id.strip()
                            
                            # Database'den ara
                            equipment = Equipment.query.filter(
                                db.or_(
                                    Equipment.id == tram_id_clean,
                                    Equipment.id == int(tram_id_clean) if tram_id_clean.isdigit() else None,
                                    Equipment.equipment_code == tram_id_clean
                                )
                            ).first()
                            
                            if equipment:
                                # Database'den gerçek veriler
                                tramvaylar.append({
                                    'id': equipment.id,
                                    'code': equipment.equipment_code or f'TRN-{tram_id_clean}',
                                    'name': equipment.name or f'Tramvay {tram_id_clean}',
                                    'location': current_project.capitalize(),
                                    'status': getattr(equipment, 'status', 'aktif'),
                                    'total_km': getattr(equipment, 'current_km', 0) or 0,
                                    'total_failures': Failure.query.filter(Failure.equipment_id == equipment.id).count() if Failure.query.count() > 0 else 0,
                                    'open_failures': Failure.query.filter(Failure.equipment_id == equipment.id, Failure.status.ilike('open')).count() if Failure.query.count() > 0 else 0,
                                    'equipment_code': equipment.equipment_code or f'TRN-{tram_id_clean}',
                                    'get_status_badge': lambda: ('success', 'Aktif')
                                })
                            else:
                                # Database'de yoksa dummy object oluştur
                                tramvaylar.append({
                                    'id': tram_id_clean,
                                    'code': f'TRN-{tram_id_clean}',
                                    'name': f'Tramvay {tram_id_clean}',
                                    'location': current_project.capitalize(),
                                    'status': 'aktif',
                                    'total_km': 0,
                                    'total_failures': 0,
                                    'open_failures': 0,
                                    'equipment_code': f'TRN-{tram_id_clean}',
                                    'get_status_badge': lambda: ('success', 'Aktif')
                                })
                except Exception as e:
                    print(f"Veriler.xlsx okuma hatası: {e}")
                    tramvaylar = []
            
            # Fallback: Database'ten al (eğer Excel yoksa)
            if not tramvaylar:
                tramvaylar = Equipment.query.all() if Equipment.query.count() > 0 else []
            
            # Get recent failures
            son_arizalar = Failure.query.order_by(Failure.created_at.desc()).limit(10).all() if Failure.query.count() > 0 else []
            
            # KPI metrics - Gerçek verilerden hesapla
            total_workorders = stats['total_workorders']
            completed_workorders = stats['bugun_tamamlanan']
            wo_completion_rate = (completed_workorders / total_workorders * 100) if total_workorders > 0 else 0
            
            # Koruyucu bakım oranı (MaintenancePlan'lar)
            total_plans = stats['total_maintenance_plans']
            preventive_ratio = (total_plans / total_workorders * 100) if total_workorders > 0 else 0
            
            # Arıza çözüm oranı (open vs total failures)
            total_failures = stats['total_failures']
            open_failures = stats['aktif_ariza']
            failure_resolution_rate = ((total_failures - open_failures) / total_failures * 100) if total_failures > 0 else 100
            
            kpi = {
                'fleet_availability': round(fleet_availability, 1),
                'failure_resolution_rate': round(failure_resolution_rate, 1),
                'wo_completion_rate': round(wo_completion_rate, 1),
                'preventive_ratio': round(preventive_ratio, 1),
                'critical_failures': open_failures,
                'total_cost': 0  # Bu veri database'de yok
            }
            
            return render_template('dashboard.html', 
                                 stats=stats, 
                                 tramvaylar=tramvaylar,
                                 son_arizalar=son_arizalar,
                                 kpi=kpi,
                                 excel_data=False)

        @app.route('/profile')
        @login_required
        def profile():
            """User profile page"""
            return render_template('profil.html', user=current_user)

        @app.route('/profile/update', methods=['POST'])
        @login_required
        def update_profile():
            """Update user profile"""
            current_user.full_name = request.form.get('full_name', current_user.full_name)
            current_user.email = request.form.get('email', current_user.email)
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('profile'))

        # Stub routes for template compatibility
        @app.route('/yeni-ariza-bildir', methods=['GET', 'POST'])
        @login_required
        def yeni_ariza_bildir():
            import pandas as pd
            from openpyxl import load_workbook
            from openpyxl.utils import get_column_letter
            from datetime import datetime
            import os
            
            project = session.get('current_project', 'belgrad')
            data_dir = os.path.join(os.path.dirname(__file__), 'data', project)
            
            # FRACAS Excel dosyasını bul
            excel_path = None
            if os.path.exists(data_dir):
                for file in os.listdir(data_dir):
                    if 'FRACAS' in file.upper() and file.endswith('.xlsx'):
                        excel_path = os.path.join(data_dir, file)
                        break
            
            if request.method == 'GET':
                # Son FRACAS ID'yi bul
                next_fracas_id = 1
                print(f"📥 GET /yeni-ariza-bildir - excel_path: {excel_path}")
                if excel_path and os.path.exists(excel_path):
                    try:
                        # FRACAS Header 1. satırda!
                        df = pd.read_excel(excel_path, sheet_name='FRACAS', header=0)
                        print(f"   📋 FRACAS sheet sütunları: {df.columns.tolist()}")
                        
                        # FRACAS ID sütununu bul
                        fracas_col = None
                        for col in df.columns:
                            if isinstance(col, str) and 'fracas' in col.lower() and 'id' in col.lower():
                                fracas_col = col
                                break
                        
                        print(f"   🔍 FRACAS ID sütunu: {fracas_col}")
                        if fracas_col:
                            # Sayısal FRACAS ID'leri çıkar
                            ids = []
                            for val in df[fracas_col].dropna():
                                try:
                                    # "BOZ-BEL25-FF-001" gibi formatları handle et
                                    if isinstance(val, str) and 'FF-' in val:
                                        num = int(val.split('FF-')[-1])
                                    elif isinstance(val, str) and '-' in val:
                                        num = int(val.split('-')[-1])
                                    else:
                                        num = int(val)
                                    ids.append(num)
                                except:
                                    pass
                            
                            print(f"   📊 Bulunan ID'ler: {sorted(ids)}") 
                            if ids:
                                next_fracas_id = max(ids) + 1
                    except Exception as e:
                        print(f"❌ FRACAS ID okuma hatası: {e}")
                
                # Tramvaylar ve sistemler
                tramvaylar = []
                sistemler = {}
                
                # Veriler.xlsx'den sistemleri yükle
                veriler_path = None
                if os.path.exists(data_dir):
                    for file in os.listdir(data_dir):
                        if 'veriler' in file.lower() and file.endswith('.xlsx'):
                            veriler_path = os.path.join(data_dir, file)
                            break
                
                if veriler_path and os.path.exists(veriler_path):
                    try:
                        wb = load_workbook(veriler_path)
                        ws = wb['Sayfa1']
                        
                        # Sistem renk tanımları
                        KIRMIZI = 'FFFF0000'
                        SARI = 'FFFFFF00'
                        MAVI = 'FF0070C0'
                        
                        # Sütun sütun tarama
                        for col in range(1, ws.max_column + 1):
                            sistem_adi = None
                            
                            for row in range(1, ws.max_row + 1):
                                cell = ws.cell(row=row, column=col)
                                value = cell.value
                                fill = cell.fill
                                
                                color_hex = None
                                if fill and fill.start_color:
                                    color_hex = str(fill.start_color.rgb) if fill.start_color.rgb else None
                                
                                # Kırmızı = Sistem
                                if color_hex == KIRMIZI and value:
                                    sistem_adi = str(value).strip()
                                    if sistem_adi not in sistemler:
                                        sistemler[sistem_adi] = {
                                            'tedarikciler': [],
                                            'alt_sistemler': []
                                        }
                                
                                # Sarı = Tedarikçi
                                elif color_hex == SARI and value and sistem_adi:
                                    sistemler[sistem_adi]['tedarikciler'].append(str(value).strip())
                                
                                # Mavi = Alt Sistem
                                elif color_hex == MAVI and value and sistem_adi:
                                    sistemler[sistem_adi]['alt_sistemler'].append(str(value).strip())
                    except Exception as e:
                        print(f"Sistem yükleme hatası: {e}")
                
                # Tramvaylar, Modüller, Arıza Sınıfları ve Arıza Kaynakları - Sayfa2'den
                modules = []  # default
                ariza_siniflari = ['Kritik', 'Yüksek', 'Orta', 'Düşük']  # default
                ariza_kaynaklari = ['Fabrika Hatası', 'Kullanıcı Hatası', 'Yıpranma', 'Bilinmiyor']  # default
                
                if os.path.exists(os.path.join(data_dir, 'Veriler.xlsx')):
                    try:
                        import unicodedata
                        
                        df_trams = pd.read_excel(os.path.join(data_dir, 'Veriler.xlsx'), sheet_name='Sayfa2', header=0)
                        print(f"Sayfa2 Sütunları: {df_trams.columns.tolist()}")  # Debug
                        
                        # Sütun adlarını normalize et (Türkçe karakterleri ASCII'ye çevir)
                        def normalize_col(col_name):
                            """Türkçe karakterleri normalize et"""
                            # Türkçe karakterleri değiştir
                            replacements = {
                                'ı': 'i', 'ş': 's', 'ç': 'c', 'ğ': 'g', 'ü': 'u', 'ö': 'o',
                                'I': 'I', 'Ş': 'S', 'Ç': 'C', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O'
                            }
                            result = col_name.strip().lower()
                            for tr, en in replacements.items():
                                result = result.replace(tr, en)
                            return result
                        
                        # tram_id sütununu bul
                        for col in df_trams.columns:
                            col_norm = normalize_col(col)
                            if 'tram' in col_norm and 'id' in col_norm:
                                tramvaylar = df_trams[col].dropna().unique().tolist()
                                tramvaylar = [str(int(t)) if isinstance(t, (int, float)) else str(t) for t in tramvaylar]
                                print(f"Tramvaylar: {tramvaylar[:5]}")  # Debug
                                break
                        
                        # Modül sütununu bul
                        for col in df_trams.columns:
                            col_norm = normalize_col(col)
                            if col_norm == 'module':
                                modules = [str(m).strip() for m in df_trams[col].dropna().unique().tolist() if str(m).strip()]
                                print(f"Modüller: {modules}")  # Debug
                                break
                        
                        # Arıza Sınıfı sütununu bul
                        for col in df_trams.columns:
                            col_norm = normalize_col(col)
                            if 'ariza' in col_norm and 'sinif' in col_norm:
                                ariza_siniflari = [str(s).strip() for s in df_trams[col].dropna().unique().tolist() if str(s).strip()]
                                print(f"Arıza Sınıfları bulundu: {ariza_siniflari}")  # Debug
                                break
                        
                        # Arıza Kaynağı sütununu bul
                        for col in df_trams.columns:
                            col_norm = normalize_col(col)
                            if 'ariza' in col_norm and 'kaynag' in col_norm:
                                ariza_kaynaklari = [str(k).strip() for k in df_trams[col].dropna().unique().tolist() if str(k).strip()]
                                print(f"Arıza Kaynakları bulundu: {ariza_kaynaklari}")  # Debug
                                break
                    except Exception as e:
                        print(f"Sayfa2 yükleme hatası: {e}")
                
                sistem_detay = {k: {'tedarikciler': list(set(v['tedarikciler'])), 'alt_sistemler': list(set(v['alt_sistemler']))} for k, v in sistemler.items()}
                
                return render_template('yeni_ariza_bildir.html', 
                                     sistem_detay=sistem_detay, 
                                     modules=modules,
                                     next_fracas_id=f"BOZ-BEL25-FF-{next_fracas_id:03d}",
                                     tramvaylar=tramvaylar,
                                     sistemler=list(sistemler.keys()),
                                     ariza_siniflari=ariza_siniflari,
                                     ariza_kaynaklari=ariza_kaynaklari)
            else:
                # POST - Excel'e kayıt et
                try:
                    form_data = request.form.to_dict()
                    print(f"\n📤 POST /yeni-ariza-bildir")
                    print(f"   📋 Gelen form alanları: {list(form_data.keys())}")
                    
                    # FRACAS ID'yi form'dan al veya hesapla
                    fracas_id = form_data.get('fracas_id', '')
                    print(f"   🔢 Form'dan gelen FRACAS ID: '{fracas_id}'")
                    if not fracas_id:
                        # FRACAS ID'yi hesapla
                        print(f"   ⚠️  Boş FRACAS ID - Excel'den hesaplanıyor...")
                        next_fracas_id = 1
                        if excel_path and os.path.exists(excel_path):
                            try:
                                # FRACAS Header 1. satırda!
                                df = pd.read_excel(excel_path, sheet_name='FRACAS', header=0)
                                fracas_col = None
                                for col in df.columns:
                                    if isinstance(col, str) and 'fracas' in col.lower() and 'id' in col.lower():
                                        fracas_col = col
                                        break
                                
                                if fracas_col:
                                    ids = []
                                    for val in df[fracas_col].dropna():
                                        try:
                                            if isinstance(val, str) and 'FF-' in val:
                                                num = int(val.split('FF-')[-1])
                                            elif isinstance(val, str) and '-' in val:
                                                num = int(val.split('-')[-1])
                                            else:
                                                num = int(val)
                                            ids.append(num)
                                        except:
                                            pass
                                    
                                    if ids:
                                        next_fracas_id = max(ids) + 1
                            except Exception as e:
                                print(f"FRACAS ID okuma hatası: {e}")
                        
                        fracas_id = f"BOZ-BEL25-FF-{next_fracas_id:03d}"
                        form_data['fracas_id'] = fracas_id
                    
                    # YENI: Arıza Listesi Excel dosyasına yaz
                    from openpyxl.styles import Border, Side, Font, PatternFill, Alignment
                    
                    ariza_listesi_dir = os.path.join(os.path.dirname(__file__), 'logs', 'ariza_listesi')
                    os.makedirs(ariza_listesi_dir, exist_ok=True)
                    
                    # Güncellik Arıza Listesi dosyasını bul
                    ariza_listesi_file = None
                    today_date = datetime.now().strftime('%Y%m%d')
                    
                    for file in os.listdir(ariza_listesi_dir):
                        if f'Ariza_Listesi_BELGRAD_{today_date}' in file and file.endswith('.xlsx'):
                            ariza_listesi_file = os.path.join(ariza_listesi_dir, file)
                            break
                    
                    # Yoksa yeni dosya oluştur
                    if not ariza_listesi_file:
                        from openpyxl import Workbook
                        wb_new = Workbook()
                        ws_new = wb_new.active
                        ws_new.title = "Ariza Listesi"
                        
                        title_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
                        title_font = Font(bold=True, size=12, color="FFFFFF")
                        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                        header_font = Font(bold=True, color="FFFFFF", size=11)
                        
                        ws_new['A1'] = "ARIZA LİSTESİ - BELGRAD PROJESİ"
                        ws_new.merge_cells('A1:R1')
                        ws_new['A1'].font = title_font
                        ws_new['A1'].fill = title_fill
                        ws_new['A1'].alignment = Alignment(horizontal="center", vertical="center")
                        ws_new.row_dimensions[1].height = 25
                        
                        ws_new['A2'] = f"Oluşturma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
                        ws_new.merge_cells('A2:R2')
                        ws_new['A2'].font = Font(italic=True, size=10)
                        ws_new['A2'].alignment = Alignment(horizontal="right")
                        
                        headers = ['FRACAS ID', 'Araç No', 'Araç Modül', 'Kilometre', 'Tarih', 'Saat', 
                                  'Sistem', 'Alt Sistem', 'Tedarikçi', 'Arıza Sınıfı', 'Arıza Kaynağı', 
                                  'Garanti Kapsamı', 'Arıza Tanımı', 'Yapılan İşlem', 'Aksiyon', 'Parça Kodu', 'Parça Adı', 'Durum']
                        
                        border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                                       top=Side(style='thin'), bottom=Side(style='thin'))
                        
                        for col_idx, header in enumerate(headers, 1):
                            cell = ws_new.cell(row=4, column=col_idx)
                            cell.value = header
                            cell.font = header_font
                            cell.fill = header_fill
                            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                            cell.border = border
                        
                        ws_new.row_dimensions[4].height = 30
                        ws_new.freeze_panes = "A5"
                        
                        ariza_listesi_file = os.path.join(ariza_listesi_dir, f"Ariza_Listesi_BELGRAD_{today_date}.xlsx")
                        wb_new.save(ariza_listesi_file)
                    
                    # Arıza Listesi dosyasına veri ekle
                    try:
                        wb = load_workbook(ariza_listesi_file)
                        ws = wb.active
                        
                        # Son dolu satırı bul
                        last_row = 4
                        for row in range(5, ws.max_row + 1):
                            if ws.cell(row=row, column=1).value:
                                last_row = row
                        
                        next_row = last_row + 1
                        
                        # Form verilerini Excel'e yaz
                        data = [
                            form_data.get('fracas_id', ''),
                            form_data.get('arac_numarasi', ''),
                            form_data.get('arac_module', ''),
                            form_data.get('arac_km', ''),
                            form_data.get('hata_tarih', ''),
                            form_data.get('hata_saat', ''),
                            form_data.get('sistem', ''),
                            form_data.get('alt_sistem', ''),
                            form_data.get('tedarikci', ''),
                            form_data.get('ariza_sinifi', ''),
                            form_data.get('ariza_kaynagi', ''),
                            form_data.get('garanti_kapsami', ''),
                            form_data.get('ariza_tanimi', ''),
                            form_data.get('yapilan_islem', ''),
                            form_data.get('aksiyon', ''),
                            form_data.get('parca_kodu', ''),
                            form_data.get('parca_adi', ''),
                            'Kaydedildi'
                        ]
                        
                        border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                                       top=Side(style='thin'), bottom=Side(style='thin'))
                        
                        for col_idx, value in enumerate(data, 1):
                            cell = ws.cell(row=next_row, column=col_idx)
                            cell.value = value
                            cell.border = border
                            cell.font = Font(size=10)
                            cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
                        
                        wb.save(ariza_listesi_file)
                        flash(f'✅ Arıza başarıyla kaydedildi: {form_data.get("fracas_id")}', 'success')
                    except Exception as e:
                        flash(f'❌ Arıza Listesi yazma hatası: {str(e)}', 'danger')
                    
                    return redirect(url_for('yeni_ariza_bildir'))
                except Exception as e:
                    flash(f'❌ Kayıt hatası: {str(e)}', 'danger')
                    return redirect(url_for('yeni_ariza_bildir'))

        @app.route('/api/parts-lookup', methods=['GET'])
        @login_required
        def parts_lookup():
            """Bileşen numarası - Nesne kısa metni arasında lookup yapıyor"""
            import pandas as pd
            
            query = request.args.get('q', '').strip().upper()
            if not query or len(query) < 2:
                return jsonify([])
            
            # Belgrad dosyasını yükle
            data_dir = os.path.join(os.path.dirname(__file__), 'data', 'belgrad')
            part_file = os.path.join(data_dir, 'GÜNCEL BELGRAD TRAMVAY 11.09.2025.XLSX')
            
            if not os.path.exists(part_file):
                return jsonify([])
            
            try:
                df = pd.read_excel(part_file)
                results = []
                
                # Bileşen numarası veya Nesne kısa metni ile ara
                for idx, row in df.iterrows():
                    bilesen_no = str(row['Bileşen numarası']).strip().upper() if pd.notna(row['Bileşen numarası']) else ''
                    nesne_metni = str(row['Nesne kısa metni']).strip().upper() if pd.notna(row['Nesne kısa metni']) else ''
                    
                    if query in bilesen_no or query in nesne_metni:
                        results.append({
                            'bilesen_no': bilesen_no,
                            'nesne_metni': nesne_metni
                        })
                        
                        if len(results) >= 10:  # Max 10 sonuç
                            break
                
                return jsonify(results)
            except Exception as e:
                print(f"Parts lookup hatası: {e}")
                return jsonify([])

        @app.route('/ekipmanlar')
        @login_required
        def ekipmanlar():
            equipment = Equipment.query.all()
            return render_template('ekipmanlar.html', equipment=equipment)

        @app.route('/arizalar')
        @login_required
        def arizalar():
            """Arıza listesi - Excel'den FRACAS verilerini yükle (Hibrid - Dinamik Sütunlar)"""
            import pandas as pd
            from routes.fracas import get_excel_path
            from datetime import datetime
            
            # Helper function
            def get_column(df, possible_names):
                """Olası kolon isimlerinden birini bul"""
                for col in df.columns:
                    for name in possible_names:
                        if name.lower() in col.lower():
                            return col
                return None
            
            def safe_get(row, possible_names, default='-'):
                """Satırdan güvenli şekilde değer getir"""
                for name in possible_names:
                    val = row.get(name)
                    if pd.notna(val) and str(val).strip() and str(val) != 'nan':
                        return str(val).strip()
                return default
            
            # Excel'den FRACAS verilerini yükle
            excel_path = get_excel_path()
            excel_data = False
            failures_list = []
            all_columns = []  # Tüm sütun adlarını tut
            column_display_names = {}  # Sütun gösterim adları
            
            if excel_path and os.path.exists(excel_path):
                try:
                    df = pd.read_excel(excel_path, sheet_name='FRACAS', header=0, engine='openpyxl')
                    df.columns = df.columns.astype(str).str.replace('\n', ' ', regex=False).str.strip()
                    
                    # Boş satırları temizle
                    fracas_col = get_column(df, ['FRACAS ID', 'Fracas Id', 'fracas_id'])
                    if fracas_col:
                        # Sadece FRACAS ID'si olan satırları tut
                        df = df[df[fracas_col].notna()].copy()
                    
                    if len(df) > 0:
                        excel_data = True
                        all_columns = list(df.columns)
                        
                        # Sütun gösterim adlarını oluştur (yeni temiz başlıklar)
                        display_mapping = {
                            'Proje': 'Proje',
                            'Araç Numarası': 'Araç No',
                            'Araç Modülü': 'Modül',
                            'Araç Kilometresi': 'Km',
                            'FRACAS ID': 'Arıza Kodu',
                            'Hata Tarih Saat': 'Tarih',
                            'Sistem': 'Sistem',
                            'Alt Sistemler': 'Alt Sistem',
                            'İlgili Tedarikçi': 'Tedarikçi',
                            'Arıza Tanımı': 'Açıklama',
                            'Arıza Sınıfı': 'Sınıf',
                            'Arıza Kaynağı': 'Kaynak',
                            'Arıza Tespitini Takiben Yapılan İşlem': 'İşlem',
                            'Aksiyon': 'Aksiyon',
                            'Garanti Kapsamı': 'Garanti',
                            'Tamir Süresi (dakika)': 'Tamir Süresi',
                            'Araç MTTR': 'MTTR Araç',
                            'Kompanent MTTR': 'MTTR Komponent',
                            'Parça Kodu': 'Parça Kodu',
                            'Parça Adı': 'Parça Adı',
                            'Adeti': 'Adet',
                            'İşçilik Maliyeti': 'Maliyet',
                            'Arıza Tipi': 'Tip',
                        }
                        
                        for col in all_columns:
                            if col in display_mapping:
                                column_display_names[col] = display_mapping[col]
                            else:
                                # Bilinmeyen sütunlar için otomatik gösterim
                                column_display_names[col] = col[:30]
                        
                        # DataFrame'i dictionary listesine dönüştür
                        for idx, (_, row) in enumerate(df.iterrows(), 1):
                            # Her sütunun değerini alalım
                            failure_dict = {'idx': idx, 'raw_data': {}}
                            
                            for col in all_columns:
                                val = row.get(col)
                                if pd.notna(val) and str(val).strip() and str(val) != 'nan':
                                    failure_dict['raw_data'][col] = str(val).strip()
                                else:
                                    failure_dict['raw_data'][col] = '-'
                            
                            # Özel işlemler (tarih, tamir süresi, vb)
                            date_val = '-'
                            for col in ['Hata Tarih Saat', 'Tarih', 'Date', '.']:
                                val = row.get(col)
                                if pd.notna(val):
                                    try:
                                        date_val = pd.Timestamp(val).strftime('%d.%m.%Y %H:%M')
                                    except:
                                        date_val = str(val).strip()
                                    if date_val != '-':
                                        break
                            failure_dict['detection_date'] = date_val
                            
                            # Tamir süresi formatlaması
                            repair_col = get_column(df, ['Tamir Süresi', 'Repair Time'])
                            if repair_col:
                                repair_time = failure_dict['raw_data'].get(repair_col, '-')
                                if repair_time != '-':
                                    try:
                                        repair_time = f"{int(float(repair_time))} dakika"
                                    except:
                                        pass
                                failure_dict['repair_time'] = repair_time
                            else:
                                failure_dict['repair_time'] = '-'
                            
                            failures_list.append(failure_dict)
                except Exception as e:
                    print(f"Excel okuma hatası: {e}")
                    import traceback
                    traceback.print_exc()
                    excel_data = False
            
            # Excel yoksa database'den çek
            if not excel_data:
                failures = Failure.query.all()
                failures_list = failures
            
            # Stats for page header
            stats = {
                'toplam': len(failures_list),
                'acik': len(failures_list),  # Excel'den tümü açık kabul et
                'devam_ediyor': 0,
                'cozuldu': 0,
            }
            
            return render_template('arizalar.html', arizalar=failures_list, failures=failures_list, excel_data=excel_data, stats=stats, columns=all_columns, column_display_names=column_display_names)

        # Alias for template compatibility
        @app.route('/ariza-listesi')
        @login_required
        def ariza_listesi():
            """Alias for arizalar"""
            return arizalar()

        @app.route('/is-emirleri')
        @login_required
        def is_emirleri():
            orders = WorkOrder.query.all()
            stats = {
                'toplam': WorkOrder.query.count(),
                'beklemede': WorkOrder.query.filter_by(status='pending').count() if hasattr(WorkOrder, 'status') else 0,
                'devam_ediyor': WorkOrder.query.filter_by(status='in_progress').count() if hasattr(WorkOrder, 'status') else 0,
                'tamamlandi': WorkOrder.query.filter_by(status='completed').count() if hasattr(WorkOrder, 'status') else 0,
            }
            return render_template('is_emirleri.html', orders=orders, stats=stats)

        @app.route('/bakim-planlari')
        @login_required
        def bakim_planlari():
            from datetime import datetime, timedelta
            
            plans = MaintenancePlan.query.all()
            
            # Tarih hesaplamaları
            today = datetime.now()
            week_later = today + timedelta(days=7)
            
            # İstatistikler
            geciken_plans = []
            bu_hafta_plans = []
            
            for plan in plans:
                if hasattr(plan, 'next_maintenance_date') and plan.next_maintenance_date:
                    if plan.next_maintenance_date < today:
                        geciken_plans.append(plan)
                    elif plan.next_maintenance_date <= week_later:
                        bu_hafta_plans.append(plan)
            
            stats = {
                'toplam': len(plans),
                'geciken': len(geciken_plans),
                'bu_hafta': len(bu_hafta_plans),
            }
            
            return render_template('bakim_planlari.html', plans=plans, stats=stats)

        @app.route('/yedek-parca')
        @login_required
        def yedek_parca():
            parts = SparePartInventory.query.all()
            stats = {
                'toplam': SparePartInventory.query.count(),
                'kritik_stok': SparePartInventory.query.filter(SparePartInventory.quantity < SparePartInventory.min_quantity).count() if hasattr(SparePartInventory, 'quantity') else 0,
            }
            return render_template('yedek_parca.html', parts=parts, stats=stats)

        @app.route('/uyarilar')
        @login_required
        def uyarilar():
            return render_template('uyarilar.html')

        @app.route('/analiz')
        @login_required
        def analiz():
            return render_template('analysis.html')

        @app.route('/raporlar')
        @login_required
        def raporlar():
            return render_template('reports.html')

        @app.route('/ayarlar')
        @login_required
        def ayarlar():
            return render_template('settings.html')

        # Additional route aliases for template compatibility
        @app.route('/arac-listesi')
        @login_required
        def arac_listesi():
            """Alias for ekipmanlar"""
            return ekipmanlar()

        @app.route('/ariza-ekle', methods=['GET', 'POST'])
        @login_required
        def ariza_ekle():
            """Alias for yeni_ariza_bildir"""
            return yeni_ariza_bildir()

        @app.route('/ariza/<int:id>')
        @login_required
        def ariza_detay(id):
            """Failure detail"""
            failure = Failure.query.get_or_404(id)
            return render_template('ariza_detay.html', failure=failure)

        @app.route('/ariza/<int:id>/guncelle', methods=['POST'])
        @login_required
        def ariza_guncelle(id):
            """Update failure"""
            failure = Failure.query.get_or_404(id)
            failure.status = request.form.get('status', failure.status)
            db.session.commit()
            flash('Failure updated', 'success')
            return redirect(url_for('ariza_detay', id=id))

        @app.route('/ekipman/<int:id>')
        @login_required
        def ekipman_detay(id):
            """Equipment detail"""
            equipment = Equipment.query.get_or_404(id)
            return render_template('ekipman_detay.html', equipment=equipment)

        @app.route('/is-emri/ekle', methods=['GET', 'POST'])
        @login_required
        def is_emri_ekle():
            """Create work order"""
            if request.method == 'POST':
                order = WorkOrder(
                    title=request.form.get('title'),
                    description=request.form.get('description'),
                    status='acik'
                )
                db.session.add(order)
                db.session.commit()
                flash('Work order created', 'success')
                return redirect(url_for('is_emirleri'))
            return render_template('is_emri_ekle.html')

        @app.route('/is-emri/<int:id>')
        @login_required
        def is_emri_detay(id):
            """Work order detail"""
            order = WorkOrder.query.get_or_404(id)
            return render_template('is_emri_detay.html', order=order)

        @app.route('/is-emri/<int:id>/guncelle', methods=['POST'])
        @login_required
        def is_emri_guncelle(id):
            """Update work order"""
            order = WorkOrder.query.get_or_404(id)
            order.status = request.form.get('status', order.status)
            db.session.commit()
            flash('Work order updated', 'success')
            return redirect(url_for('is_emri_detay', id=id))

        @app.route('/bakim-plani/ekle', methods=['GET', 'POST'])
        @login_required
        def bakim_plani_ekle():
            """Create maintenance plan"""
            if request.method == 'POST':
                plan = MaintenancePlan(
                    name=request.form.get('name'),
                    description=request.form.get('description'),
                    is_active=True
                )
                db.session.add(plan)
                db.session.commit()
                flash('Maintenance plan created', 'success')
                return redirect(url_for('bakim_planlari'))
            return render_template('bakim_plani_ekle.html')

        @app.route('/dokuman-listesi')
        @login_required
        def dokuman_listesi():
            """Documents list"""
            return render_template('dokuman_listesi.html')

        @app.route('/dokuman/ekle', methods=['GET', 'POST'])
        @login_required
        def dokuman_ekle():
            """Add document"""
            if request.method == 'POST':
                flash('Document added', 'success')
                return redirect(url_for('dokuman_listesi'))
            return render_template('dokuman_ekle.html')

        @app.route('/dokuman/<int:id>')
        @login_required
        def dokuman_detay(id):
            """Document detail"""
            return render_template('dokuman_detay.html')

        @app.route('/dokuman/<int:id>/indir')
        @login_required
        def dokuman_indir(id):
            """Download document"""
            flash('Document download', 'info')
            return redirect(url_for('dokuman_listesi'))

        @app.route('/kullanicilar')
        @login_required
        def kullanicilar():
            """Users list"""
            users = User.query.all()
            return render_template('kullanicilar.html', users=users)

        @app.route('/kullanici/ekle', methods=['GET', 'POST'])
        @login_required
        def kullanici_ekle():
            """Add user"""
            if request.method == 'POST':
                user = User(
                    username=request.form.get('username'),
                    email=request.form.get('email'),
                    full_name=request.form.get('full_name'),
                    role='user'
                )
                user.set_password(request.form.get('password'))
                db.session.add(user)
                db.session.commit()
                flash('User created', 'success')
                return redirect(url_for('kullanicilar'))
            return render_template('kullanici-ekle.html')

        @app.route('/proje-sec')
        def proje_sec():
            """Select project"""
            current_project = session.get('current_project', 'belgrad')
            # Add metadata to projects
            projects_with_data = []
            for project in PROJECTS:
                project_data = project.copy()
                project_data['has_fracas'] = False
                project_data['vehicle_count'] = 0
                project_data['failure_count'] = 0
                project_data['open_failures'] = 0
                projects_with_data.append(project_data)
            
            return render_template('proje_sec.html', projects=projects_with_data, current_project=current_project)

        @app.route('/proje-degistir/<project_code>')
        @login_required
        def proje_degistir(project_code):
            """Change project"""
            project = next((p for p in PROJECTS if p['code'] == project_code), None)
            
            if project:
                session['current_project'] = project_code
                session['project_code'] = project_code.lower()
                session['project_name'] = f"{project['flag']} {project['name']}"
                flash(f"Proje değiştirildi: {project['flag']} {project['name']}", 'success')
            else:
                flash('Geçersiz proje!', 'error')
            
            return redirect(url_for('dashboard'))

        @app.route('/profil-guncelle', methods=['POST'])
        @login_required
        def profil_guncelle():
            """Update profile"""
            return update_profile()

        @app.route('/audit-log')
        @login_required
        def audit_log():
            """Audit log"""
            return render_template('audit-log.html')
        @app.route('/tramvay-km')
        @login_required
        def tramvay_km():
            """Tram kilometer tracking - Veriler.xlsx Sayfa2'den tram_id'leri çek, database'den values"""
            import pandas as pd
            import os
            
            # Project folder'ını belirle
            project_code = session.get('project_code', 'belgrad').lower()
            project_folder = os.path.join('data', project_code)
            excel_path = os.path.join(project_folder, 'Veriler.xlsx')
            
            tram_ids = []
            equipments = []
            
            # Excel'den tramvay ID'lerini çek
            if os.path.exists(excel_path):
                try:
                    # Sayfa2 (index 1) oku
                    df = pd.read_excel(excel_path, sheet_name=1, header=0, engine='openpyxl')
                    
                    # tram_id sütununu bul
                    if 'tram_id' in df.columns:
                        for idx, row in df.iterrows():
                            tram_id = str(row['tram_id']).strip() if pd.notna(row['tram_id']) else None
                            if tram_id:
                                tram_ids.append(tram_id)
                except Exception as e:
                    print(f"Excel okuma hatası: {str(e)}")
            
            # Tram ID'ler için database'den equipment'ları çek
            if tram_ids:
                # ID'ler integer olabilir, string olabilir - her ikiyle de ara
                for tram_id in tram_ids:
                    # String olarak ara
                    equipment = Equipment.query.filter(
                        db.or_(
                            Equipment.id == tram_id,
                            Equipment.id == int(tram_id) if tram_id.isdigit() else None,
                            Equipment.equipment_code == str(tram_id)
                        )
                    ).first()
                    
                    # Bulunamadıysa dummy object oluştur (veriler halen database'de ama equipment oluşturulmamış olabilir)
                    if equipment:
                        equipments.append(equipment)
                    else:
                        # Dummy object - bu tramvay henüz kayıt edilmemiş
                        class TramObj:
                            def __init__(self, code):
                                self.id = code
                                self.equipment_code = code
                                self.current_km = 0
                                self.monthly_km = 0
                                self.notes = ''
                                self.last_update = None
                        
                        equipments.append(TramObj(tram_id))
            
            # Veri bulunamadıysa fallback
            if not equipments:
                equipments_db = Equipment.query.filter_by(equipment_type='Tramvay').all()
                equipments = equipments_db if equipments_db else []
            
            # İstatistikleri hesapla
            stats = {
                'toplam_tramvay': len(equipments),
                'toplam_km': sum(getattr(e, 'current_km', 0) or 0 for e in equipments),
                'ortalama_km': sum(getattr(e, 'current_km', 0) or 0 for e in equipments) // len(equipments) if equipments else 0,
                'max_km': max([getattr(e, 'current_km', 0) or 0 for e in equipments]) if equipments else 0,
            }
            
            return render_template('tramvay_km.html', 
                                 stats=stats,
                                 equipments=equipments,
                                 project_name=session.get('project_name', 'Belgrad'))

        @app.route('/tramvay-km/guncelle', methods=['POST'])
        @login_required
        def tramvay_km_guncelle():
            """Update tram km"""
            try:
                tram_id = request.form.get('tram_id')
                current_km = request.form.get('current_km', 0)
                notes = request.form.get('notes', '')
                
                # Equipment tablosunda ara
                equipment = Equipment.query.get(tram_id)
                
                # Bulunamadıysa oluştur
                if not equipment:
                    equipment = Equipment(
                        id=tram_id,
                        equipment_code=tram_id,
                        name=f'Tramvay {tram_id}',
                        equipment_type='Tramvay',
                        current_km=0,
                        monthly_km=0,
                        notes=''
                    )
                    db.session.add(equipment)
                
                # Verileri güncelle
                try:
                    equipment.current_km = int(current_km) if current_km else 0
                    equipment.notes = notes
                    db.session.commit()
                    flash(f'✅ {equipment.equipment_code or tram_id} KM bilgileri kaydedildi', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'❌ Kaydedilme hatası: {str(e)}', 'danger')
            except Exception as e:
                flash(f'❌ Hata: {str(e)}', 'danger')
            
            return redirect(url_for('tramvay_km'))

        @app.route('/tramvay-km/toplu-guncelle', methods=['POST'])
        @login_required
        def tramvay_km_toplu_guncelle():
            """Bulk update tram km"""
            try:
                updates = request.get_json()
                count = 0
                errors = []
                
                for tram_id, data in updates.items():
                    try:
                        # Equipment tablosunda ara
                        equipment = Equipment.query.get(tram_id)
                        
                        # Bulunamadıysa oluştur
                        if not equipment:
                            equipment = Equipment(
                                id=tram_id,
                                equipment_code=tram_id,
                                name=f'Tramvay {tram_id}',
                                equipment_type='Tramvay',
                                current_km=0,
                                monthly_km=0,
                                notes=''
                            )
                            db.session.add(equipment)
                        
                        # Mevcut KM güncelle
                        if 'current_km' in data and data['current_km']:
                            try:
                                equipment.current_km = int(float(data['current_km']))
                            except:
                                errors.append(f"{tram_id}: Geçersiz KM değeri")
                                continue
                        
                        # Notlar güncelle
                        if 'notes' in data:
                            equipment.notes = str(data['notes']).strip()
                        
                        count += 1
                    except Exception as e:
                        errors.append(f"Tramvay {tram_id}: {str(e)}")
                
                db.session.commit()
                
                message = f'✅ {count} araç başarıyla kaydedildi'
                if errors:
                    message += f' ({len(errors)} hata)'
                
                return jsonify({'success': True, 'message': message}), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': f'❌ Hata: {str(e)}'}), 500

        @app.route('/servis-durumu', methods=['GET', 'POST'])
        @login_required
        def servis_durumu():
            """Service status"""
            from datetime import timedelta, datetime
            from openpyxl import load_workbook
            import os
            
            # POST isteği - Yeni durum kayıt et
            if request.method == 'POST':
                try:
                    tarih = request.form.get('tarih')
                    tramvay_id = request.form.get('tramvay_id')
                    durum = request.form.get('durum')
                    sistem = request.form.get('sistem', '')
                    aciklama = request.form.get('aciklama', '')
                    
                    # ServiceStatus modeli varsa kayıt et
                    try:
                        from models import ServiceStatus
                        # Mevcut kaydı kontrol et
                        existing = ServiceStatus.query.filter_by(
                            tram_id=tramvay_id,
                            date=tarih
                        ).first()
                        
                        if existing:
                            existing.status = durum
                            existing.sistem = sistem
                            existing.aciklama = aciklama
                        else:
                            new_status = ServiceStatus(
                                tram_id=tramvay_id,
                                date=tarih,
                                status=durum,
                                sistem=sistem,
                                aciklama=aciklama
                            )
                            db.session.add(new_status)
                        
                        db.session.commit()
                        flash(f'Durum başarıyla kaydedildi: {tramvay_id} - {tarih}', 'success')
                    except Exception as e:
                        flash(f'Durum kaydı hatası: {str(e)}', 'warning')
                    
                    return redirect(request.url)
                except Exception as e:
                    flash(f'Bir hata oluştu: {str(e)}', 'danger')
                    return redirect(request.url)
            
            equipments = Equipment.query.all()
            today_str = datetime.now().strftime('%Y-%m-%d')
            
            # Tramvaylar - Excel'den yükle (İstatistik hesaplaması için gerekli)
            excel_path = None
            project = session.get('current_project', 'belgrad')
            data_dir = os.path.join(os.path.dirname(__file__), 'data', project)
            
            if os.path.exists(data_dir):
                for file in os.listdir(data_dir):
                    if file.endswith('.xlsx') and 'Veriler' in file:
                        excel_path = os.path.join(data_dir, file)
                        break
                # Veriler.xlsx bulamazsa ilk xlsx'i al
                if not excel_path:
                    for file in os.listdir(data_dir):
                        if file.endswith('.xlsx'):
                            excel_path = os.path.join(data_dir, file)
                            break
            
            tramvaylar = []
            if excel_path and os.path.exists(excel_path):
                try:
                    wb = load_workbook(excel_path)
                    
                    # Sayfa2'den tram_id'leri oku (öncelikli)
                    if 'Sayfa2' in wb.sheetnames:
                        ws = wb['Sayfa2']
                        headers = []
                        
                        # Header'ı oku (1. satır)
                        header_row = list(ws.iter_rows(min_row=1, max_row=1, values_only=True))[0]
                        tram_id_col = None
                        
                        # tram_id sütununu bul
                        for idx, header in enumerate(header_row):
                            if header and 'tram' in str(header).lower():
                                tram_id_col = idx
                                break
                        
                        if tram_id_col is not None:
                            # Tramvay ID'lerini oku (tekrar edenleri görmezden gel)
                            seen_trams = set()
                            for row in ws.iter_rows(min_row=2, values_only=True):
                                tram_id = row[tram_id_col] if row[tram_id_col] else None
                                if tram_id:
                                    tram_str = str(int(tram_id)) if isinstance(tram_id, (int, float)) else str(tram_id)
                                    if tram_str not in seen_trams:
                                        seen_trams.add(tram_str)
                                        tram_obj = type('Tram', (), {
                                            'id': tram_str,
                                            'weekly_status': {}
                                        })()
                                        tramvaylar.append(tram_obj)
                    
                    # Eğer Sayfa2'den tramvay bulunamadıysa, tüm sheet'leri kontrol et
                    if not tramvaylar:
                        for sheet_name in wb.sheetnames:
                            ws = wb[sheet_name]
                            headers = []
                            
                            # Header'ı oku (1. satır)
                            header_row = list(ws.iter_rows(min_row=1, max_row=1, values_only=True))[0]
                            tram_id_col = None
                            
                            # tram_id sütununu bul
                            for idx, header in enumerate(header_row):
                                if header and 'tram' in str(header).lower():
                                    tram_id_col = idx
                                    break
                            
                            if tram_id_col is not None:
                                # Tramvay ID'lerini oku
                                for row in ws.iter_rows(min_row=2, values_only=True):
                                    tram_id = row[tram_id_col] if row[tram_id_col] else None
                                    if tram_id:
                                        tram_obj = type('Tram', (), {
                                            'id': str(int(tram_id)) if isinstance(tram_id, (int, float)) else str(tram_id),
                                            'weekly_status': {}
                                        })()
                                        tramvaylar.append(tram_obj)
                                break  # İlk sheet'i bulduktan sonra çık
                except Exception as e:
                    print(f"Excel okuşta hata: {e}")
                    pass
            
            # Eğer Excel'den yüklenemezse, veritabanından yükle
            if not tramvaylar:
                for eq in equipments:
                    tram_obj = type('Tram', (), {
                        'id': str(eq.id),
                        'weekly_status': {}
                    })()
                    tramvaylar.append(tram_obj)
            
            # SİSTEM, TEDARİKÇİ ve ALT SİSTEM verilerini Veriler.xlsx'ten çek (renk bazlı)
            sistemler = {}  # {sistem_adi: {tedarikçiler: [...], alt_sistemler: [...]}}
            
            veriler_path = None
            if os.path.exists(data_dir):
                for file in os.listdir(data_dir):
                    if 'veriler' in file.lower() and file.endswith('.xlsx'):
                        veriler_path = os.path.join(data_dir, file)
                        break
            
            if veriler_path and os.path.exists(veriler_path):
                try:
                    wb = load_workbook(veriler_path)
                    ws = wb['Sayfa1']  # Sayfa1'i aç
                    
                    # Renk tanımları
                    KIRMIZI = 'FFFF0000'  # SİSTEM
                    SARI = 'FFFFFF00'     # TEDARİKÇİ
                    MAVI = 'FF0070C0'     # ALT SİSTEM
                    
                    # Her sütunu kontrol et (sütun başına bir sistem)
                    for col in range(1, ws.max_column + 1):
                        sistem_adi = None
                        
                        # Sütundaki tüm satırları tara
                        for row in range(1, ws.max_row + 1):
                            cell = ws.cell(row=row, column=col)
                            value = cell.value
                            fill = cell.fill
                            
                            color_hex = None
                            if fill and fill.start_color:
                                color_hex = str(fill.start_color.rgb) if fill.start_color.rgb else None
                            
                            # Kırmızı renkli ise sistem bulundu (row 1'de)
                            if color_hex == KIRMIZI and value:
                                sistem_adi = str(value).strip()
                                if sistem_adi not in sistemler:
                                    sistemler[sistem_adi] = {
                                        'tedarikçiler': set(),
                                        'alt_sistemler': set()
                                    }
                            
                            # Sarı renkli ise tedarikçi
                            elif color_hex == SARI and value and sistem_adi:
                                sistemler[sistem_adi]['tedarikçiler'].add(str(value).strip())
                            
                            # Mavi renkli ise alt sistem
                            elif color_hex == MAVI and value and sistem_adi:
                                sistemler[sistem_adi]['alt_sistemler'].add(str(value).strip())
                    
                    # Set'leri list'e çevir ve sort et
                    sistemler = {
                        k: {
                            'tedarikçiler': sorted(list(v['tedarikçiler'])),
                            'alt_sistemler': sorted(list(v['alt_sistemler']))
                        }
                        for k, v in sistemler.items()
                    }
                except Exception as e:
                    print(f"Sistem verileri yüklenirken hata: {e}")
                    sistemler = {}
            
            import json
            sistemler_json = json.dumps(sistemler)
            print(f"\n{'='*60}")
            print(f"EXCEL'DEN ÇEKILEN SİSTEMLER:")
            print(f"{'='*60}")
            print(f"Toplam Sistem Sayısı: {len(sistemler)}")
            for sistem_adi, data in sistemler.items():
                print(f"\n📌 {sistem_adi}")
                if data.get('tedarikçiler'):
                    print(f"   Tedarikçiler: {', '.join(data['tedarikçiler'])}")
                if data.get('alt_sistemler'):
                    print(f"   Alt Sistemler: {', '.join(data['alt_sistemler'])}")
            print(f"{'='*60}\n")
            
            # ========== İSTATİSTİKLER - Tramvaylar yüklendikten sonra hesapla ==========
            stats = {
                'Servis': 0,
                'Servis Dışı': 0,
                'İşletme Kaynaklı Servis Dışı': 0,
                'erisebilirlik': '0%'
            }
            
            try:
                from models import ServiceStatus
                today_records = ServiceStatus.query.filter_by(date=today_str).all()
                
                servis_count = 0
                servis_disi_count = 0
                isletme_kaynak_count = 0
                
                for record in today_records:
                    if record.status == 'Servis':
                        servis_count += 1
                    elif record.status == 'Servis Dışı':
                        servis_disi_count += 1
                    elif record.status == 'İşletme Kaynaklı Servis Dışı':
                        isletme_kaynak_count += 1
                
                stats['Servis'] = servis_count
                stats['Servis Dışı'] = servis_disi_count
                stats['İşletme Kaynaklı Servis Dışı'] = isletme_kaynak_count
                
                # Erişilebilirlik hesapla: (Toplam araçlar - Servis Dışı - İşletme Kaynaklı) / Toplam
                total_tramvaylar = len(tramvaylar) if tramvaylar else 0
                if total_tramvaylar > 0:
                    available = total_tramvaylar - servis_disi_count - isletme_kaynak_count
                    erisebilirlik_percent = (available / total_tramvaylar) * 100
                    stats['erisebilirlik'] = f"{erisebilirlik_percent:.1f}%"
                
                print(f"İstatistikler (Bugün - {today_str}):")
                print(f"  Serviste: {servis_count}")
                print(f"  Servis Dışı: {servis_disi_count}")
                print(f"  İşletme Kaynaklı: {isletme_kaynak_count}")
                print(f"  Toplam Araçlar: {total_tramvaylar}")
                print(f"  Erişilebilirlik: {stats['erisebilirlik']}\n")
                
            except Exception as e:
                print(f"ServiceStatus hatası: {e}\n")
                stats = {
                    'Servis': 0,
                    'Servis Dışı': 0,
                    'İşletme Kaynaklı Servis Dışı': 0,
                    'erisebilirlik': '0%'
                }
            # ========== İSTATİSTİKLER SONU ==========
            
            # Son 7 günü hesapla
            last_7_days = []
            for i in range(6, -1, -1):
                date = datetime.now() - timedelta(days=i)
                last_7_days.append(date.strftime('%Y-%m-%d'))
            
            # 7 günlük status matrix - veritabanından çek (varsa)
            status_matrix = {}
            tram_ids_list = [t.id if hasattr(t, 'id') else str(t) for t in tramvaylar]
            
            # Eğer ServiceStatus modeli varsa sorgu yap
            if hasattr(db, 'session'):
                try:
                    from models import ServiceStatus
                    for tram_id in tram_ids_list:
                        status_matrix[tram_id] = {}
                        for date in last_7_days:
                            status_record = ServiceStatus.query.filter_by(
                                tram_id=tram_id,
                                date=date
                            ).first()
                            if status_record:
                                status_matrix[tram_id][date] = (
                                    status_record.status if hasattr(status_record, 'status') else 'Unknown',
                                    status_record.sistem if hasattr(status_record, 'sistem') else '',
                                    status_record.aciklama if hasattr(status_record, 'aciklama') else ''
                                )
                except:
                    pass
            
            # Bir önceki günün verileri al (form önceden doldurma için)
            yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            yesterday_data = {}
            try:
                from models import ServiceStatus
                yesterday_records = ServiceStatus.query.filter_by(date=yesterday_str).all()
                for record in yesterday_records:
                    yesterday_data[record.tram_id] = {
                        'status': record.status if hasattr(record, 'status') else '',
                        'sistem': record.sistem if hasattr(record, 'sistem') else '',
                        'aciklama': record.aciklama if hasattr(record, 'aciklama') else ''
                    }
            except:
                pass
            
            return render_template('servis_durumu.html', 
                                 stats=stats, 
                                 tramvaylar=tramvaylar,
                                 tram_ids=tram_ids_list,
                                 last_7_days=last_7_days,
                                 dates=last_7_days,
                                 status_matrix=status_matrix,
                                 today=datetime.now().strftime('%Y-%m-%d'),
                                 sistemler=sistemler,
                                 sistemler_json=sistemler_json,
                                 project_name=session.get('project_name', 'Belgrad'),
                                 yesterday_data=yesterday_data)

        @app.route('/servis-durumu/guncelle', methods=['POST'])
        @login_required
        def servis_durumu_guncelle():
            """Update service status"""
            flash('Service status updated', 'success')
            return redirect(url_for('servis_durumu'))

        @app.route('/servis-durumu/toplu-servise-al', methods=['POST'])
        @login_required
        def servis_durumu_toplu_servise_al():
            """Bulk send to service"""
            try:
                from datetime import datetime
                from models import ServiceStatus
                
                today_str = datetime.now().strftime('%Y-%m-%d')
                data = request.get_json()
                tram_ids = data.get('tram_ids', [])
                
                for tram_id in tram_ids:
                    # Mevcut kaydı kontrol et
                    existing = ServiceStatus.query.filter_by(
                        tram_id=str(tram_id),
                        date=today_str
                    ).first()
                    
                    if existing:
                        existing.status = 'Servis'
                    else:
                        new_status = ServiceStatus(
                            tram_id=str(tram_id),
                            date=today_str,
                            status='Servis',
                            sistem='',
                            aciklama='Toplu servise alındı'
                        )
                        db.session.add(new_status)
                
                db.session.commit()
                return jsonify({'success': True, 'message': f'{len(tram_ids)} araç servise alındı'}), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': str(e)}), 400

        @app.route('/api/copy_previous_day', methods=['POST'])
        @login_required
        def api_copy_previous_day():
            """Önceki günün verilerini bugüne kopyala"""
            try:
                data = request.get_json()
                yesterday_data = data.get('yesterday_data', {})
                
                if not yesterday_data:
                    return jsonify({'success': False, 'message': 'Dün\'ün veri yok'}), 400
                
                # Bugünkü tarihi al
                from datetime import datetime, timedelta, date
                today = date.today()
                yesterday = today - timedelta(days=1)
                
                today_str = today.strftime('%Y-%m-%d')
                yesterday_str = yesterday.strftime('%Y-%m-%d')
                
                # Tüm araçlar için dünün durumunu bugüne kopyala
                from models import ServiceStatus
                
                count = 0
                for tram_id, yesterday_record in yesterday_data.items():
                    tram_str = str(tram_id)
                    
                    # Bugün için zaten kayıt varsa kontrol et
                    existing = ServiceStatus.query.filter_by(
                        tram_id=tram_str,
                        date=today_str
                    ).first()
                    
                    if existing:
                        # Mevcut kaydı güncelle
                        existing.status = yesterday_record.get('status', '')
                        existing.sistem = yesterday_record.get('sistem', '')
                        existing.aciklama = yesterday_record.get('aciklama', '') + ' (Dünden kopyalandı)'
                    else:
                        # Yeni kayıt oluştur
                        new_record = ServiceStatus(
                            tram_id=tram_str,
                            date=today_str,
                            status=yesterday_record.get('status', ''),
                            sistem=yesterday_record.get('sistem', ''),
                            aciklama=yesterday_record.get('aciklama', '') + ' (Dünden kopyalandı)'
                        )
                        db.session.add(new_record)
                    count += 1
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': f'✅ {count} araç dünün durumuna göre güncellendi'
                }), 200
                
            except Exception as e:
                db.session.rollback()
                print(f"Hata: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({'success': False, 'message': str(e)}), 400

        @app.route('/servis-durumu/indir')
        @login_required
        def servis_durumu_indir():
            """Download service status"""
            flash('Service status downloaded', 'info')
            return redirect(url_for('servis_durumu'))

        @app.route('/yedek-parca/ekle', methods=['GET', 'POST'])
        @login_required
        def yedek_parca_ekle():
            """Add spare part"""
            if request.method == 'POST':
                part = SparePartInventory(
                    part_name=request.form.get('part_name'),
                    part_code=request.form.get('part_code')
                )
                db.session.add(part)
                db.session.commit()
                flash('Spare part added', 'success')
                return redirect(url_for('yedek_parca'))
            return render_template('yedek-parca-ekle.html')

        # Error handlers
        @app.errorhandler(404)
        def not_found(error):
            return render_template('404.html'), 404

        @app.errorhandler(500)
        def internal_error(error):
            db.session.rollback()
            return render_template('500.html'), 500

        print('create_app finished')
        print(f'App object type: {type(app)}')
        print(f'App object: {app}')
        return app
        
    except Exception as e:
        print(f'CRITICAL ERROR in create_app: {e}')
        import traceback
        traceback.print_exc()
        return None


def init_sample_data(app):
    """Initialize sample data"""
    with app.app_context():
        db.create_all()
        
        if User.query.filter_by(username='admin').first():
            return
        
        admin = User(
            username='admin',
            email='admin@bozankaya-tramway.com',
            full_name='System Administrator',
            role='admin',
            department='IT',
            employee_id='EMP001',
            hourly_rate=50
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Sample data initialized successfully!')


if __name__ == '__main__':
    app = create_app()
    if app:
        init_sample_data(app)
    print("\nSSH Takip System starting...")
    print("URL: http://localhost:5000")
    print("User: admin / admin123\n")
    if app:
        app.run(debug=True, port=5000)
