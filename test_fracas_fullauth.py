"""Tam authenticated FRACAS render test"""
import os, sys, io
sys.path.insert(0, os.path.dirname(__file__))
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app

app = create_app()

with app.test_client() as client:
    with app.app_context():
        from models import db, User, Role
        db.create_all()
        
        # Doğru password hash ile test user oluştur
        test_user = User.query.filter_by(username='fracas_test').first()
        if not test_user:
            test_user = User(username='fracas_test', email='fracas@test.com')
            test_user.set_password('Test123!')  # Doğru hash
            test_user.is_active = True
            user_role = Role.query.filter_by(name='operator').first()
            if user_role:
                test_user.roles.append(user_role)
            else:
                admin_role = Role.query.filter_by(name='admin').first()
                if admin_role:
                    test_user.roles.append(admin_role)
            db.session.add(test_user)
            db.session.commit()
            print("[+] Test user oluşturuldu: fracas_test / Test123!")
        else:
            test_user.set_password('Test123!')
            db.session.commit()
            print("[*] Test user zaten var, password güncellendi")
        
        # 1. LOGIN
        print("\n=== LOGIN ===")
        resp = client.post('/login', data={
            'username': 'fracas_test',
            'password': 'Test123!'
        }, follow_redirects=False)
        print(f"Login status: {resp.status_code}")
        print(f"Redirect: {resp.headers.get('Location', 'YOK')}")
        
        if resp.status_code in (301, 302):
            print("[+] Login redirect - başarılı!")
        
        # Session kontrol
        with client.session_transaction() as sess:
            print(f"Session keys: {list(sess.keys())}")
            user_id = sess.get('_user_id', 'YOK')
            print(f"_user_id (flask-login): {user_id}")
        
        # 2. FRACAS sayfasına git
        for project in ['belgrad', 'timisoara']:
            print(f"\n=== FRACAS {project.upper()} ===")
            resp = client.get(f'/fracas/?project={project}', follow_redirects=True)
            html = resp.data.decode('utf-8', errors='replace')
            
            print(f"Status: {resp.status_code}")
            print(f"HTML boyutu: {len(html)} bytes")
            
            # Sayfa title kontrolü
            import re
            title_match = re.search(r'<title>(.*?)</title>', html)
            title = title_match.group(1) if title_match else 'BULUNAMADI'
            print(f"Title: {title}")
            
            # Kritik element kontrolleri
            checks = {
                'Login sayfasına redirect': 'Giriş - Bozankaya' in title,
                'FRACAS sayfası': 'FRACAS' in title,
                'data_available=False (uyarı)': 'Excel Dosyası Bulunamadı' in html,
                '<canvas> paretoModule': '<canvas id="paretoModuleChart"' in html,
                '<canvas> paretoSupplier': '<canvas id="paretoSupplierChart"' in html,
                '<canvas> monthlyTrend': '<canvas id="monthlyTrendChart"' in html,
                'new Chart() çağrısı': 'new Chart(' in html,
                'pareto_labels_module verisi': '"MC"' in html or '"T"' in html,
                'chart.js CDN (extra)': 'cdn.jsdelivr.net/npm/chart.js"' in html,
                'chart.js 4.4.0 (base)': 'chart.js@4.4.0' in html,
                'Filtreler paneli': 'Filtreler' in html,
            }
            
            print("\n--- KONTROLLER ---")
            for desc, result in checks.items():
                status = "OK" if result else "FAIL"
                print(f"  [{status}] {desc}")
            
            # HTML'i kaydet
            fname = f'fracas_auth_rendered_{project}.html'
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"\nHTML kaydedildi: {fname}")
