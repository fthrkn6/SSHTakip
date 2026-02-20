#!/usr/bin/env python3
"""Uygulama API'sini test et - 1556 gerçekte gösteriyor mu?"""
import sys
sys.path.insert(0, '.')

from app import create_app
from models import User, Equipment, ServiceStatus
from datetime import date
import json

app = create_app()

with app.app_context():
    project = 'belgrad'
    today = str(date.today())
    
    print("\n" + "="*100)
    print("🌐 API RESPONSE TEST")
    print("="*100 + "\n")
    
    # Test Admin kullanıcısı yarat
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@test.com',
            full_name='Test Admin',
            role='admin'
        )
        admin.set_password('admin')
        try:
            db.session.add(admin)
            db.session.commit()
        except:
            pass
    
    # Test client oluştur
    with app.test_client() as client:
        # 1. Login (session setup)
        print("1️⃣  Login işlemi")
        with client.session_transaction() as sess:
            sess['user_id'] = admin.id if admin else 1
            sess['current_project'] = 'belgrad'
        print("   ✅ Session oluşturuldu\n")
        
        # 2. Dashboard API'sini test et
        print("2️⃣  /api/equipment Dashboard API'si")
        response = client.get('/api/equipment', json={'project': 'belgrad'})
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            equipment_codes = [eq['equipment_code'] for eq in data.get('equipment', [])]
            equipment_codes = sorted(equipment_codes)
            print(f"   Araç Sayısı: {len(equipment_codes)}")
            print(f"   1556 var mı? {'✅ EVET' if '1556' in equipment_codes else '❌ HAYIR'}")
            print(f"   Araçlar: {equipment_codes[:5]}... ({len(equipment_codes)} toplam)")
        else:
            print(f"   ❌ Hata: {response.data}")
        print()
        
        # 3. ServiceStatus API'sini test et  
        print("3️⃣  /api/service-status Servis Durumu API'si")
        response = client.get(f'/api/service-status?date={today}')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            records = data.get('data', {})  # veya records olabilir
            tram_ids = sorted(list(records.keys()) if isinstance(records, dict) else [r['tram_id'] for r in records])
            print(f"   Kayıt Sayısı: {len(tram_ids)}")
            print(f"   1556 var mı? {'✅ EVET' if '1556' in tram_ids else '❌ HAYIR'}")
            if tram_ids:
                print(f"   Araçlar: {tram_ids[:5]}... ({len(tram_ids)} toplam)")
        else:
            print(f"   Hata: {response.data}")
        print()
    
    print("="*100)
    print("✅ TÜM TESTLER TAMAMLANDI")
    print("="*100 + "\n")
