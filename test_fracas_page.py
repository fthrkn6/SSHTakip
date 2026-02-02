import os
import sys
sys.path.insert(0, 'c:\\Users\\ferki\\Desktop\\bozankaya_ssh_takip')

from app import create_app, db
from models import User

app = create_app()

# Test client oluştur
with app.test_client() as client:
    # Login yap
    with app.app_context():
        # Kullanıcı oluştur
        user = User.query.filter_by(username='ferki').first()
        if not user:
            user = User(username='ferki', email='ferki@example.com', role='admin')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
    
    # Login request
    response = client.post('/login', data={
        'username': 'ferki',
        'password': 'password'
    }, follow_redirects=True)
    
    print(f"Login Status: {response.status_code}")
    
    # FRACAS sayfasını ziyaret et
    response = client.get('/fracas/')
    print(f"FRACAS Status: {response.status_code}")
    
    if response.status_code == 200:
        # Sayfada "data_available" var mı kontrol et
        if b'Excel' in response.data and b'Bulunamad' in response.data:
            print("❌ data_available false - Excel bulunamadı uyarısı gösteriliyor")
        elif b'FRACAS Analiz Dashboard' in response.data:
            print("✅ FRACAS sayfası gösteriliyor")
            if b'Toplam' in response.data or b'Reliability' in response.data:
                print("✅ İstatistikler gösteriliyor")
            else:
                print("❌ İstatistikler gösterilmiyor")
    else:
        print(f"❌ FRACAS sayfası yüklenemedi: {response.status_code}")
        print(response.data.decode('utf-8')[:500])
