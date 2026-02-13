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
from routes.dashboard import bp as dashboard_bp
import os
import shutil
import tempfile


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
        app.register_blueprint(dashboard_bp)

        # ==================== ROUTES ====================

        @app.route('/')
        def index():
            if current_user.is_authenticated:
                return redirect(url_for('dashboard.index'))
            return redirect(url_for('login'))

        @app.route('/login', methods=['GET', 'POST'])
        def login():
            if current_user.is_authenticated:
                return redirect(url_for('dashboard'))
            
            if request.method == 'POST':
                try:
                    username = request.form.get('username')
                    password = request.form.get('password')
                    print(f"[LOGIN] Attempting login with username: {username}")
                    
                    user = User.query.filter_by(username=username).first()
                    print(f"[LOGIN] User found: {user is not None}")
                    
                    if user and user.check_password(password):
                        print(f"[LOGIN] Password correct for {username}")
                        login_user(user, remember=request.form.get('remember'))
                        user.last_login = datetime.now()
                        db.session.commit()
                        print(f"[LOGIN] User {username} logged in successfully")
                        
                        # Set project from form selection or default to belgrad
                        selected_project = request.form.get('project', 'belgrad')
                        if selected_project and selected_project in [p['code'] for p in PROJECTS]:
                            project = next((p for p in PROJECTS if p['code'] == selected_project), None)
                            if project:
                                session['current_project'] = selected_project
                                session['project_code'] = selected_project
                                session['project_name'] = f"{project['flag']} {project['name']}"
                                print(f"[LOGIN] Project set to: {selected_project}")
                        else:
                            session['current_project'] = 'belgrad'
                            session['project_code'] = 'belgrad'
                            session['project_name'] = '🇷🇸 Belgrad'
                        
                        next_page = request.args.get('next')
                        if next_page and next_page.startswith('/'):
                            return redirect(next_page)
                        return redirect(url_for('dashboard.index'))
                    else:
                        print(f"[LOGIN] Invalid password for {username}")
                        flash('Invalid username or password', 'danger')
                except Exception as e:
                    print(f"[LOGIN] Error during login: {type(e).__name__}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    flash(f'Login error: {str(e)}', 'danger')
            
            return render_template('login.html')

        @app.route('/logout')
        @login_required
        def logout():
            logout_user()
            flash('You have been logged out.', 'success')
            return redirect(url_for('login'))

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
                # Son FRACAS ID'yi Arıza Listesi'nden bul
                import tempfile
                import time
                next_fracas_id = 1
                
                ariza_listesi_dir = os.path.join(os.path.dirname(__file__), 'logs', project, 'ariza_listesi')
                os.makedirs(ariza_listesi_dir, exist_ok=True)
                temp_dir = tempfile.gettempdir()
                
                ariza_listesi_file = os.path.join(ariza_listesi_dir, f"Ariza_Listesi_{project.upper()}.xlsx")
                
                if os.path.exists(ariza_listesi_file):
                    try:
                        # Excel'i direkt aç (temp'e kopyalamadan)
                        from openpyxl import load_workbook
                        wb = load_workbook(ariza_listesi_file, data_only=True)
                        ws = wb.active
                        
                        # A sütununda FRACAS ID'leri ara (Row 5'ten başla, Row 4 header)
                        ids = []
                        for row in range(5, ws.max_row + 1):
                            cell_val = ws.cell(row=row, column=1).value
                            if cell_val and isinstance(cell_val, str) and 'FF-' in str(cell_val):
                                try:
                                    num = int(str(cell_val).split('FF-')[-1])
                                    ids.append(num)
                                    print(f"   ✓ Row {row}: {cell_val} -> {num}")
                                except:
                                    pass
                        
                        wb.close()
                        
                        if ids:
                            next_fracas_id = max(ids) + 1
                        else:
                            next_fracas_id = 1
                    except Exception as e:
                        next_fracas_id = 1
                
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
                        pass
                
                # Tramvaylar, Modüller, Arıza Sınıfları ve Arıza Kaynakları - Sayfa2'den
                modules = []  # default
                ariza_siniflari = ['Kritik', 'Yüksek', 'Orta', 'Düşük']  # default
                ariza_kaynaklari = ['Fabrika Hatası', 'Kullanıcı Hatası', 'Yıpranma', 'Bilinmiyor']  # default
                ariza_tipleri = []  # default
                
                if os.path.exists(os.path.join(data_dir, 'Veriler.xlsx')):
                    try:
                        import unicodedata
                        
                        df_trams = pd.read_excel(os.path.join(data_dir, 'Veriler.xlsx'), sheet_name='Sayfa2', header=0)

                        
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

                                break
                        
                        # Modül sütununu bul
                        for col in df_trams.columns:
                            col_norm = normalize_col(col)
                            if col_norm == 'module':
                                modules = [str(m).strip() for m in df_trams[col].dropna().unique().tolist() if str(m).strip()]

                                break
                        
                        # Arıza Sınıfı sütununu bul
                        for col in df_trams.columns:
                            col_norm = normalize_col(col)
                            if 'ariza' in col_norm and 'sinif' in col_norm:
                                ariza_siniflari = [str(s).strip() for s in df_trams[col].dropna().unique().tolist() if str(s).strip()]

                                break
                        
                        # Arıza Kaynağı sütununu bul
                        for col in df_trams.columns:
                            col_norm = normalize_col(col)
                            if 'ariza' in col_norm and 'kaynag' in col_norm:
                                ariza_kaynaklari = [str(k).strip() for k in df_trams[col].dropna().unique().tolist() if str(k).strip()]
                                break
                        
                        # Arıza Tipi sütununu bul
                        ariza_tipleri = []
                        for col in df_trams.columns:
                            col_norm = normalize_col(col)
                            if 'ariza' in col_norm and 'tip' in col_norm:
                                ariza_tipleri = [str(t).strip() for t in df_trams[col].dropna().unique().tolist() if str(t).strip()]
                                ariza_tipleri = sorted(list(set(ariza_tipleri)))
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
                                     ariza_kaynaklari=ariza_kaynaklari,
                                     ariza_tipleri=ariza_tipleri)
            else:
                # POST - Excel'e kayıt et
                try:
                    form_data = request.form.to_dict()
                    print(f"\n📤 POST /yeni-ariza-bildir")
                    print(f"   📋 Gelen form alanları: {list(form_data.keys())}")
                    
                    # FRACAS ID'yi form'dan al veya hesapla
                    fracas_id = form_data.get('fracas_id', '').strip()
                    print(f"   🔢 Form'dan gelen FRACAS ID: '{fracas_id}'")
                    
                    # Arıza Listesi dosyasından FRACAS ID'yi hesapla (YALNIzCA BURADAN)
                    import tempfile
                    import time
                    
                    ariza_listesi_dir = os.path.join(os.path.dirname(__file__), 'logs', project, 'ariza_listesi')
                    os.makedirs(ariza_listesi_dir, exist_ok=True)
                    
                    temp_dir = tempfile.gettempdir()
                    ariza_listesi_file = os.path.join(ariza_listesi_dir, f"Ariza_Listesi_{project.upper()}.xlsx")
                    
                    # FRACAS ID hesapla (YALNIzCA Arıza Listesi'nden - TEMP'TEN OKU)
                    next_fracas_num = 1
                    if os.path.exists(ariza_listesi_file):
                        try:
                            # Main dosyayı temp'e kopyala (lock'u çözmek için)
                            temp_read_file = os.path.join(temp_dir, f"Ariza_check_{int(time.time())}.xlsx")
                            shutil.copy(ariza_listesi_file, temp_read_file)
                            time.sleep(0.2)
                            
                            # Temp'ten oku
                            wb_check = load_workbook(temp_read_file, data_only=True)
                            ws_check = wb_check.active
                            
                            # A sütununda (FRACAS ID) max numarayı bul
                            print(f"   📊 Arıza Listesi max row: {ws_check.max_row}")
                            for row in range(5, ws_check.max_row + 1):
                                cell_val = ws_check.cell(row=row, column=1).value
                                if cell_val:
                                    try:
                                        if isinstance(cell_val, str) and 'FF-' in cell_val:
                                            num = int(cell_val.split('FF-')[-1])
                                            next_fracas_num = max(next_fracas_num, num + 1)
                                            print(f"   ✓ Row {row}: {cell_val} -> next will be {next_fracas_num}")
                                    except Exception as e:
                                        pass
                            wb_check.close()
                            os.remove(temp_read_file)
                            print(f"   ✅ FRACAS ID hesaplandı: {next_fracas_num}")
                        except Exception as e:
                            print(f"   ❌ FRACAS ID okuma hatası: {e}")
                            next_fracas_num = 1
                    
                    if not fracas_id:
                        fracas_id = f"BOZ-BEL25-FF-{next_fracas_num:03d}"
                        print(f"   ✓ Hesaplanan FRACAS ID: {fracas_id}")
                        form_data['fracas_id'] = fracas_id
                    
                    # YENI: Arıza Listesi Excel dosyasına yaz
                    from openpyxl.styles import Border, Side, Font, PatternFill, Alignment
                    import shutil
                    
                    ariza_listesi_dir = os.path.join(os.path.dirname(__file__), 'logs', project, 'ariza_listesi')
                    os.makedirs(ariza_listesi_dir, exist_ok=True)
                    
                    # Güncellik Arıza Listesi dosyasını bul
                    today_date = datetime.now().strftime('%Y%m%d')
                    ariza_listesi_file = os.path.join(ariza_listesi_dir, f"Ariza_Listesi_{project.upper()}.xlsx")
                    
                    # Temp klasörü tanımla (tüm işlemler için)
                    import tempfile
                    import time
                    temp_dir = tempfile.gettempdir()
                    
                    # Yoksa yeni dosya oluştur (temp'te, sonra taşı)
                    if not os.path.exists(ariza_listesi_file):
                        temp_file = os.path.join(temp_dir, f"Ariza_Listesi_{project.upper()}_temp_{int(time.time())}.xlsx")
                        
                        from openpyxl import Workbook
                        wb_new = Workbook()
                        ws_new = wb_new.active
                        ws_new.title = "Ariza Listesi"
                        
                        title_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
                        title_font = Font(bold=True, size=12, color="FFFFFF")
                        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                        header_font = Font(bold=True, color="FFFFFF", size=11)
                        
                        project_display = [p['name'] for p in PROJECTS if p['code'] == project][0] if project in [p['code'] for p in PROJECTS] else project.upper()
                        ws_new['A1'] = f"ARIZA LİSTESİ - {project_display.upper()} PROJESİ"
                        ws_new.merge_cells('A1:U1')
                        ws_new['A1'].font = title_font
                        ws_new['A1'].fill = title_fill
                        ws_new['A1'].alignment = Alignment(horizontal="center", vertical="center")
                        ws_new.row_dimensions[1].height = 25
                        
                        ws_new['A2'] = f"Oluşturma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
                        ws_new.merge_cells('A2:U2')
                        ws_new['A2'].font = Font(italic=True, size=10)
                        ws_new['A2'].alignment = Alignment(horizontal="right")
                        
                        headers = ['FRACAS ID', 'Araç No', 'Araç Modül', 'Kilometre', 'Tarih', 'Saat', 
                                  'Sistem', 'Alt Sistem', 'Tedarikçi', 'Arıza Sınıfı', 'Arıza Kaynağı', 'Arıza Tipi',
                                  'Garanti Kapsamı', 'Arıza Tanımı', 'Yapılan İşlem', 'Aksiyon', 'Parça Kodu', 'Parça Adı', 'Parça Seri No', 'Adet',
                                  'Tamir Başlama Tarihi', 'Tamir Başlama Saati', 'Tamir Bitişi Tarihi', 'Tamir Bitişi Saati', 'Tamir Süresi', 'MTTR (dk)',
                                  'Servise Veriliş Tarihi', 'Servise Veriliş Saati', 'Durum', 'Personel Sayısı']
                        
                        # Sütun genişlikleri (30 sütun)
                        column_widths = [13, 10, 12, 10, 12, 10, 12, 12, 12, 14, 14, 18, 12, 20, 14, 10, 12, 12, 12, 10, 15, 14, 14, 14, 14, 12, 14, 14, 10, 12]
                        for idx, width in enumerate(column_widths, 1):
                            ws_new.column_dimensions[get_column_letter(idx)].width = width
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
                        
                        # Temp'e kaydet
                        wb_new.save(temp_file)
                        wb_new.close()
                        
                        # Final konuma taşı
                        time.sleep(0.5)
                        try:
                            shutil.move(temp_file, ariza_listesi_file)
                            print(f"   ✓ Arıza Listesi dosyası oluşturuldu: {ariza_listesi_file}")
                        except:
                            # Zaten var olabilir, kontrol et
                            if not os.path.exists(ariza_listesi_file) and os.path.exists(temp_file):
                                shutil.copy(temp_file, ariza_listesi_file)
                                os.remove(temp_file)
                    
                    # Arıza Listesi dosyasına veri ekle (Temp dosya ile atomic işlem)
                    try:
                        # Ana dosyayı temp'e kopyala
                        temp_write_file = os.path.join(temp_dir, f"Ariza_write_{today_date}_{int(time.time())}.xlsx")
                        shutil.copy(ariza_listesi_file, temp_write_file)
                        time.sleep(0.3)
                        
                        # Temp dosyada aç, veri yaz
                        wb = load_workbook(temp_write_file)
                        ws = wb.active
                        
                        # Son satırı bul (Header 4. satırdan sonra)
                        next_row = 5
                        for row in range(5, ws.max_row + 100):
                            if not ws.cell(row=row, column=1).value:
                                next_row = row
                                break
                        else:
                            next_row = ws.max_row + 1
                        
                        print(f"   📝 Veri yazılacak satır: {next_row}")
                        
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
                            form_data.get('ariza_tipi', ''),
                            form_data.get('garanti_kapsami', ''),
                            form_data.get('ariza_tanimi', ''),
                            form_data.get('yapilan_islem', ''),
                            form_data.get('aksiyon', ''),
                            form_data.get('parca_kodu', ''),
                            form_data.get('parca_adi', ''),
                            form_data.get('parca_seri_no', ''),
                            form_data.get('adet', ''),
                            form_data.get('tamir_baslama_tarih', ''),
                            form_data.get('tamir_baslama_saati', ''),
                            form_data.get('tamir_bitisi_tarih', ''),
                            form_data.get('tamir_bitisi_saati', ''),
                            form_data.get('tamir_suresi', ''),
                            form_data.get('mttr', ''),
                            form_data.get('servise_verilis_tarih', ''),
                            form_data.get('servise_verilis_saat', ''),
                            'Kaydedildi',
                            form_data.get('personel_sayisi', '')
                        ]
                        
                        border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                                       top=Side(style='thin'), bottom=Side(style='thin'))
                        
                        # Zebra pattern: Row 5 = beyaz, Row 6 = gri, vb.
                        is_white = (next_row - 5) % 2 == 0
                        white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
                        gray_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
                        fill = white_fill if is_white else gray_fill
                        
                        for col_idx, value in enumerate(data, 1):
                            cell = ws.cell(row=next_row, column=col_idx)
                            cell.value = value
                            cell.border = border
                            cell.font = Font(size=10)
                            cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
                            cell.fill = fill
                        
                        # Temp dosyaya kaydet
                        wb.save(temp_write_file)
                        wb.close()
                        time.sleep(0.5)
                        
                        # Eski dosyayı sil, temp'i ana konuma taşı (atomic)
                        if os.path.exists(ariza_listesi_file):
                            os.remove(ariza_listesi_file)
                        
                        shutil.move(temp_write_file, ariza_listesi_file)
                        time.sleep(0.3)
                        
                        print(f"   ✅ Arıza kaydedildi: {form_data.get('fracas_id')} -> Satır {next_row}")
                        flash(f'✅ Arıza başarıyla kaydedildi: {form_data.get("fracas_id")}', 'success')
                    except Exception as e:
                        flash(f'❌ Arıza Listesi yazma hatası: {str(e)}', 'danger')
                    
                    return redirect(url_for('yeni_ariza_bildir'))
                except Exception as e:
                    flash(f'❌ Kayıt hatası: {str(e)}', 'danger')
                    return redirect(url_for('yeni_ariza_bildir'))

        @app.route('/ariza-listesi-veriler')
        @login_required
        def ariza_listesi_veriler():
            """Arıza Listesi sayfası - logs/{project}/ariza_listesi/'den verileri oku ve göster"""
            import pandas as pd
            import numpy as np
            
            project = session.get('current_project', 'belgrad')
            
            # Birincil konum: logs/{project}/ariza_listesi/
            ariza_listesi_dir = os.path.join(os.path.dirname(__file__), 'logs', project, 'ariza_listesi')
            
            ariza_listesi_file = None
            use_sheet = None
            header_row = 0
            
            if os.path.exists(ariza_listesi_dir):
                # logs/{project}/ariza_listesi/ klasöründen ara
                for file in os.listdir(ariza_listesi_dir):
                    if file.endswith('.xlsx') and not file.startswith('~$'):
                        ariza_listesi_file = os.path.join(ariza_listesi_dir, file)
                        use_sheet = 'Ariza Listesi'
                        header_row = 3
                        break
            
            # Fallback: data/{project}/Veriler.xlsx
            if not ariza_listesi_file:
                veriler_file = os.path.join(os.path.dirname(__file__), 'data', project, 'Veriler.xlsx')
                if os.path.exists(veriler_file):
                    ariza_listesi_file = veriler_file
                    use_sheet = 'Veriler'
                    header_row = 0
            
            rows = []
            row_count = 0
            file_date = 'Bilinmiyor'
            
            if ariza_listesi_file and os.path.exists(ariza_listesi_file):
                try:
                    # Excel'i oku
                    df = pd.read_excel(ariza_listesi_file, sheet_name=use_sheet, header=header_row)
                    
                    # Verileri hazırla
                    for idx, row in df.iterrows():
                        row_data = list(row)
                        # Boş satırları atla
                        if any(row_data):  # Eğer satırda herhangi bir veri varsa
                            # NaN değerlerini 'Yok' ile değiştir, sayıları int'e çevir
                            processed_row = []
                            for i, val in enumerate(row_data):
                                # Personel Sayısı (index 29) ve Parça Adedi (index 19) NaN ise 0 yap
                                if (i == 19 or i == 29) and (pd.isna(val) or (isinstance(val, float) and np.isnan(val))):
                                    processed_row.append(0)
                                # Parça Kodu (16) ve Parça Adı (17) NaN ise 'Yok' yap
                                elif (i == 16 or i == 17) and (pd.isna(val) or (isinstance(val, float) and np.isnan(val))):
                                    processed_row.append('Yok')
                                # Float değerini int'e çevir (1.0 → 1) - NaN değilse
                                elif isinstance(val, float) and not (pd.isna(val) or np.isnan(val)) and val == int(val):
                                    processed_row.append(int(val))
                                else:
                                    processed_row.append(val)
                            
                            # Eğer Parça Kodu (16) ve Parça Adı (17) her ikisi de 'Yok' ise, Adedi (19) 0 yap
                            if processed_row[16] == 'Yok' and processed_row[17] == 'Yok':
                                processed_row[19] = 0
                            
                            rows.append(processed_row)
                    
                    row_count = len(rows)
                    
                    # Dosya tarihi
                    file_mtime = os.path.getmtime(ariza_listesi_file)
                    file_date = datetime.fromtimestamp(file_mtime).strftime('%d.%m.%Y %H:%M')
                    
                    print(f"✅ Arıza Listesi yüklendi: {row_count} satır")
                    
                except Exception as e:
                    print(f"❌ Arıza Listesi okuma hatası: {e}")
                    flash(f'⚠️ Veri okuma hatası: {str(e)}', 'warning')
            else:
                flash(f'⚠️ Bugünün Arıza Listesi dosyası bulunamadı', 'warning')
            
            return render_template('ariza_listesi.html', 
                                 rows=rows, 
                                 row_count=row_count,
                                 file_date=file_date,
                                 enumerate=enumerate)

        @app.route('/ariza-listesi-veriler/process', methods=['POST'])
        @login_required
        def ariza_listesi_veriler_process():
            """Arıza Listesi verilerini işle (şimdilik onay sonrası mesaj göster)"""
            
            print("📤 Arıza Listesi işlem başlıyor...")
            
            try:
                project = session.get('current_project', 'belgrad')
                ariza_listesi_dir = os.path.join(os.path.dirname(__file__), 'logs', project, 'ariza_listesi')
                ariza_listesi_file = os.path.join(ariza_listesi_dir, f"Ariza_Listesi_{project.upper()}.xlsx")
                
                if not os.path.exists(ariza_listesi_file):
                    flash('❌ Arıza Listesi dosyası bulunamadı', 'danger')
                    return redirect(url_for('ariza_listesi_veriler'))
                
                flash(f'✅ Veriler başarıyla işlendi!', 'success')
                
            except Exception as e:
                flash(f'❌ İşlem hatası: {str(e)}', 'danger')
            
            return redirect(url_for('ariza_listesi_veriler'))

        @app.route('/ariza-listesi-veriler/export')
        @login_required
        def ariza_listesi_veriler_export():
            """Arıza Listesi Excel dosyasını indir"""
            import pandas as pd
            
            project = session.get('current_project', 'belgrad')
            ariza_listesi_dir = os.path.join(os.path.dirname(__file__), 'logs', project, 'ariza_listesi')
            ariza_listesi_file = os.path.join(ariza_listesi_dir, f"Ariza_Listesi_{project.upper()}.xlsx")
            
            if not os.path.exists(ariza_listesi_file):
                flash('❌ Dosya bulunamadı', 'danger')
                return redirect(url_for('ariza_listesi_veriler'))
            
            try:
                from flask import send_file
                return send_file(
                    ariza_listesi_file,
                    as_attachment=True,
                    download_name=f"Ariza_Listesi_{project.upper()}.xlsx",
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            except Exception as e:
                flash(f'❌ İndirme hatası: {str(e)}', 'danger')
                return redirect(url_for('ariza_listesi_veriler'))

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
            """Redirect to ariza_listesi_veriler page"""
            return redirect(url_for('ariza_listesi_veriler'))

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
            import json
            
            # Bakım verilerini yükle
            maintenance_file = os.path.join(os.path.dirname(__file__), 'data', 'belgrad', 'maintenance.json')
            maintenance_data = {}
            
            if os.path.exists(maintenance_file):
                with open(maintenance_file, 'r', encoding='utf-8') as f:
                    maintenance_data = json.load(f)
            
            return render_template('bakim_planlari.html', maintenance_data=maintenance_data)
        
        @app.route('/api/bakim-plani-tablosu')
        @login_required
        def bakim_plani_tablosu():
            """Tüm KM noktalarında yapılması gereken bakımları döndür"""
            import json
            
            # maintenance.json'u yükle
            maintenance_file = os.path.join(os.path.dirname(__file__), 'data', 'belgrad', 'maintenance.json')
            maintenance_data = {}
            
            if os.path.exists(maintenance_file):
                with open(maintenance_file, 'r', encoding='utf-8') as f:
                    maintenance_data = json.load(f)
            
            # Bakım seviyelerini sırala (70K ve 140K hariç - bunlar sadece specific KM'lerde)
            sorted_levels = sorted([(k, v['km']) for k, v in maintenance_data.items() 
                                   if k not in ['70K', '140K']], key=lambda x: x[1])
            
            # Tüm KM noktaları için bakımları hesapla
            schedule = []
            max_km = 300000
            
            for km in range(0, max_km + 1000, 1000):
                applicable = []
                
                for level_name, level_km in sorted_levels:
                    if km > 0 and km % level_km == 0:
                        works = maintenance_data[level_name].get('works', [])
                        works_count = len([w for w in works if w.startswith('BOZ')])
                        applicable.append({
                            'level': level_name,
                            'km': level_km,
                            'works': works_count,
                            'ratio': km // level_km
                        })
                
                # SPECIAL: 72000 KM'de 70K bakımını da ekle
                if km == 72000:
                    works = maintenance_data.get('70K', {}).get('works', [])
                    works_count = len([w for w in works if w.startswith('BOZ')])
                    applicable.append({
                        'level': '70K',
                        'km': 70000,
                        'works': works_count,
                        'ratio': 1  # Special case olduğu için 1
                    })
                
                if applicable:
                    total_works = sum(m['works'] for m in applicable)
                    
                    # Kapsamı belirle
                    if total_works >= 30:
                        scope = 'urgent'
                        scope_label = 'ÇOK KAPSAMLI'
                    elif total_works >= 20:
                        scope = 'heavy'
                        scope_label = 'KAPSAMLI'
                    else:
                        scope = 'normal'
                        scope_label = 'ORTA'
                    
                    schedule.append({
                        'km': km,
                        'maintenances': [f"{m['level']} (×{m['ratio']})" for m in applicable],
                        'maintenance_detail': applicable,
                        'total_works': total_works,
                        'scope': scope,
                        'scope_label': scope_label
                    })
            
            return jsonify(schedule)
        
        @app.route('/api/bakim-verileri')
        @login_required
        def bakim_verileri():
            """Tüm araçların bakım durumunu tablo formatında döndür (Equipment.current_km'den dinamik olarak)"""
            import json
            from datetime import datetime
            
            # Bakım verilerini yükle
            maintenance_file = os.path.join(os.path.dirname(__file__), 'data', 'belgrad', 'maintenance.json')
            maintenance_data = {}
            
            if os.path.exists(maintenance_file):
                with open(maintenance_file, 'r', encoding='utf-8') as f:
                    maintenance_data = json.load(f)
            
            # Bakım KM'lerini sırayla al
            maintenance_levels = sorted([k for k in maintenance_data.keys()], 
                                       key=lambda x: int(x.replace('K', '')) * 1000)
            
            # KM verilerini al - FALLBACK şu anda Equipment tablosundan priorite alıyor
            km_file = os.path.join(os.path.dirname(__file__), 'data', 'belgrad', 'km_data.json')
            tram_km_fallback = {}
            
            if os.path.exists(km_file):
                with open(km_file, 'r', encoding='utf-8') as f:
                    try:
                        km_data = json.load(f)
                        # KM verileri doğrudan tram ID'leri içeriyor
                        tram_km_fallback = {k: v for k, v in km_data.items() if k and isinstance(v, dict) and 'current_km' in v}
                    except:
                        pass
            
            # Tüm araçları ekipman tablosundan al (DİNAMİK KAYNAĞIMIZ)
            result = []
            equipment_list = Equipment.query.all()
            
            # Eğer Equipment boşsa, KM verilerinden tram ID'lerini al (fallback)
            if not equipment_list and tram_km_fallback:
                equipment_list = []
                for tram_id in sorted(tram_km_fallback.keys()):
                    tram_obj = type('Equipment', (), {
                        'id': tram_id,
                        'name': f'Tramvay {tram_id}',
                        'current_km': tram_km_fallback[tram_id].get('current_km', 0)
                    })()
                    equipment_list.append(tram_obj)
            
            for eq in equipment_list:
                tram_id = str(eq.id)
                # Equipment tablosundan KM'yi al (DİNAMİK)
                current_km = getattr(eq, 'current_km', 0) or 0
                
                # Fallback: Eğer Equipment.current_km boşsa, km_data.json'dan al
                if not current_km and tram_id in tram_km_fallback:
                    current_km = tram_km_fallback[tram_id].get('current_km', 0)
                
                # Tüm bakım seviyelerini hesapla ve en yakınını bul
                all_maintenances = {}
                nearest_maintenance = None
                min_km_left = float('inf')
                
                for level in maintenance_levels:
                    level_km = int(level.replace('K', '')) * 1000
                    
                    # Bu bakımın katları: 6K = 6, 12, 18, 24... (limit 300K)
                    max_km = 300000  # 300K
                    multiples = []
                    
                    for i in range(1, (max_km // level_km) + 2):
                        km_value = level_km * i
                        multiples.append(km_value)
                    
                    # Sonraki bakım tarihi bul
                    next_due = None
                    for km_value in multiples:
                        if km_value > current_km:
                            next_due = km_value
                            break
                    
                    # Status belirle
                    if next_due is None:
                        # Tüm katları geçmiş
                        status = 'overdue'
                        km_left = current_km - multiples[-1]
                    else:
                        km_left = next_due - current_km
                        if km_left <= 0:
                            status = 'overdue'
                        elif km_left <= 500:
                            status = 'urgent'
                        elif km_left <= 2000:
                            status = 'warning'
                        else:
                            status = 'normal'
                    
                    maint_info = {
                        'level': level,
                        'level_km': level_km,
                        'next_km': next_due or multiples[-1],
                        'km_left': km_left if km_left > 0 else 0,
                        'status': status,
                        'multiples': multiples,
                        'works': maintenance_data.get(level, {}).get('works', [])
                    }
                    
                    all_maintenances[level] = maint_info
                    
                    # En yakını bul (pozitif km_left ile en küçük olanı; eşitse en yüksek level olanı)
                    if km_left > 0:
                        if km_left < min_km_left:
                            min_km_left = km_left
                            nearest_maintenance = maint_info
                        elif km_left == min_km_left and level_km > nearest_maintenance.get('level_km', 0):
                            # Eşit km_left'te daha yüksek level bakımını seç (18K > 6K vs)
                            nearest_maintenance = maint_info
                
                # Eğer hiç pozitif km_left yoksa (tümü geçmiş), en son bakımı al
                if nearest_maintenance is None:
                    nearest_maintenance = all_maintenances[maintenance_levels[-1]]
                
                # SPECIAL: Eğer next_km 72K'nin katıysa (72, 144, 216, 288K), 70K işlerini ekle
                next_km = nearest_maintenance.get('next_km', 0)
                is_70k_due = False
                if next_km > 0 and next_km % 72000 == 0 and 'all_maintenances' in locals():
                    # 70K işlerini ekle
                    is_70k_due = True
                    # 70K works sayısını al
                    seventy_k_works = len([w for w in maintenance_data.get('70K', {}).get('works', []) if w.startswith('BOZ')])
                    
                    # Eğer nearest_maintenance'da 70K yoksa, works sayısını artır
                    if 'level' in nearest_maintenance and nearest_maintenance['level'] != '70K':
                        # 70K'ı works'e not et (UI'da gösterilecek)
                        original_works = nearest_maintenance.get('works', [])
                        nearest_maintenance['has_70k'] = True
                        nearest_maintenance['additional_70k_works'] = seventy_k_works
                
                result.append({
                    'tram_id': tram_id,
                    'tram_name': eq.name if hasattr(eq, 'name') else tram_id,
                    'current_km': current_km,
                    'nearest_maintenance': nearest_maintenance,
                    'all_maintenances': all_maintenances
                })
            
            return jsonify({
                'tramps': result,
                'levels': maintenance_levels,
                'headers': maintenance_levels
            })

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
            """Dokümanlar - Proje spesifik filtreleme"""
            from models import TechnicalDocument
            import os
            
            current_project = session.get('current_project', 'belgrad')
            
            # Kategori ve tip filtreleri
            category = request.args.get('category', 'all')
            doc_type = request.args.get('type', 'all')
            
            # Doküman sorguksı
            query = TechnicalDocument.query.filter_by(project_code=current_project, is_active=True)
            
            if category != 'all':
                query = query.filter_by(category=category)
            if doc_type != 'all':
                query = query.filter_by(document_type=doc_type)
            
            dokumanlar = query.order_by(TechnicalDocument.created_at.desc()).all()
            
            # İstatistikler
            stats = {
                'toplam': len(dokumanlar),
                'kilavuz': len([d for d in dokumanlar if d.document_type == 'manual']),
                'sema': len([d for d in dokumanlar if d.document_type == 'schematic']),
                'prosedur': len([d for d in dokumanlar if d.document_type == 'procedure'])
            }
            
            return render_template('dokumanlar.html', 
                                 dokumanlar=dokumanlar, 
                                 stats=stats,
                                 category=category,
                                 doc_type=doc_type)

        @app.route('/dokuman/ekle', methods=['GET', 'POST'])
        @login_required
        def dokuman_ekle():
            """Yeni doküman ekle (Proje spesifik)"""
            from models import TechnicalDocument, Equipment
            
            current_project = session.get('current_project', 'belgrad')
            
            if request.method == 'POST':
                title = request.form.get('title')
                document_type = request.form.get('document_type')
                category = request.form.get('category')
                description = request.form.get('description')
                version = request.form.get('version', '1.0')
                
                # Yeni doküman kodu oluştur
                from datetime import datetime
                document_code = f"{current_project.upper()}-DOC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                dokuman = TechnicalDocument(
                    document_code=document_code,
                    project_code=current_project,
                    title=title,
                    document_type=document_type,
                    category=category,
                    description=description,
                    version=version,
                    is_active=True
                )
                
                db.session.add(dokuman)
                db.session.commit()
                
                flash(f'✅ Doküman başarıyla eklendi: {document_code}', 'success')
                return redirect(url_for('dokuman_listesi'))
            
            # GET - Form göster
            ekipmanlar = Equipment.query.all()
            return render_template('dokuman_ekle.html', ekipmanlar=ekipmanlar)

        @app.route('/dokuman/<int:id>')
        @login_required
        def dokuman_detay(id):
            """Doküman detayı (Proje spesifik)"""
            from models import TechnicalDocument
            
            current_project = session.get('current_project', 'belgrad')
            dokuman = TechnicalDocument.query.filter_by(id=id, project_code=current_project).first()
            
            if not dokuman:
                flash('❌ Doküman bulunamadı', 'danger')
                return redirect(url_for('dokuman_listesi'))
            
            # View count artır
            dokuman.view_count += 1
            dokuman.last_accessed = datetime.now()
            db.session.commit()
            
            return render_template('dokuman_detay.html', dokuman=dokuman)

        @app.route('/dokuman/<int:id>/indir')
        @login_required
        def dokuman_indir(id):
            """Doküman indir (Proje spesifik)"""
            from models import TechnicalDocument
            
            current_project = session.get('current_project', 'belgrad')
            dokuman = TechnicalDocument.query.filter_by(id=id, project_code=current_project).first()
            
            if not dokuman or not dokuman.file_path:
                flash('❌ Dosya bulunamadı', 'danger')
                return redirect(url_for('dokuman_listesi'))
            
            dokuman.download_count += 1
            db.session.commit()
            
            try:
                return send_file(dokuman.file_path, as_attachment=True, download_name=dokuman.file_name)
            except Exception as e:
                flash(f'❌ Dosya indirme hatası: {str(e)}', 'danger')
                return redirect(url_for('dokuman_detay', id=id))

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
            
            return redirect(url_for('dashboard.index'))

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
                        
                        alt_sistem = request.form.get('alt_sistem', '')
                        
                        if existing:
                            existing.status = durum
                            existing.sistem = sistem
                            existing.alt_sistem = alt_sistem
                            existing.aciklama = aciklama
                        else:
                            new_status = ServiceStatus(
                                tram_id=tramvay_id,
                                date=tarih,
                                status=durum,
                                sistem=sistem,
                                alt_sistem=alt_sistem,
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
                                    status_record.alt_sistem if hasattr(status_record, 'alt_sistem') else '',
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
                        'alt_sistem': record.alt_sistem if hasattr(record, 'alt_sistem') else '',
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
                data = request.get_json(force=True, silent=True)
                
                if not data:
                    return jsonify({'success': False, 'message': 'Geçersiz istek (JSON gerekli)'}), 400
                
                tram_ids = data.get('tram_ids', [])
                
                if not tram_ids:
                    return jsonify({'success': False, 'message': 'Araç listesi boş'}), 400
                
                for tram_id in tram_ids:
                    # Mevcut kaydı kontrol et
                    existing = ServiceStatus.query.filter_by(
                        tram_id=str(tram_id),
                        date=today_str
                    ).first()
                    
                    if existing:
                        existing.status = 'Servis'
                        existing.alt_sistem = ''
                    else:
                        new_status = ServiceStatus(
                            tram_id=str(tram_id),
                            date=today_str,
                            status='Servis',
                            sistem='',
                            alt_sistem='',
                            aciklama='Toplu servise alındı'
                        )
                        db.session.add(new_status)
                
                db.session.commit()
                return jsonify({'success': True, 'message': f'{len(tram_ids)} araç servise alındı'}), 200
            except Exception as e:
                db.session.rollback()
                logger.error(f'toplu-servise-al error: {str(e)}')
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
                        existing.aciklama = yesterday_record.get('aciklama', '')
                    else:
                        # Yeni kayıt oluştur
                        new_record = ServiceStatus(
                            tram_id=tram_str,
                            date=today_str,
                            status=yesterday_record.get('status', ''),
                            sistem=yesterday_record.get('sistem', ''),
                            aciklama=yesterday_record.get('aciklama', '')
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
            import traceback
            # Log the full error
            print("\n" + "="*80)
            print("INTERNAL SERVER ERROR (500)")
            print("="*80)
            print(f"Error Type: {type(error)}")
            print(f"Error Message: {str(error)}")
            print(f"\nFull Traceback:")
            print(traceback.format_exc())
            print("="*80 + "\n")
            
            db.session.rollback()
            
            # Try to render the error template, if that fails, show plain text
            try:
                return render_template('500.html'), 500
            except:
                return f"""
                <html>
                    <body>
                        <h1>500 - Internal Server Error</h1>
                        <p>An error occurred. Check the server logs for details.</p>
                        <p><a href="/">Go back</a></p>
                    </body>
                </html>
                """, 500

        @app.before_request
        def log_request():
            """Log all incoming requests"""
            print(f"\n>> {request.method} {request.path} - IP: {request.remote_addr}")

        @app.after_request
        def log_response(response):
            """Log all responses"""
            print(f"<< {response.status_code} {response.status} - {request.path}")
            return response

        print('create_app finished')
        print(f'App object type: {type(app)}')
        print(f'App object: {app}')
        return app
        
    except Exception as e:
        # Critical error occurred during app initialization
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
    # Cloud ve local deployment için PORT ayarı
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
