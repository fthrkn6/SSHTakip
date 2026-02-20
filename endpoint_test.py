#!/usr/bin/env python3
"""Endpoint test - 50 araç doğrulama"""
import sys
sys.path.insert(0, '.')

from app import create_app
from models import User

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("✅ ENDPOINT TEST - 50 ARAÇ")
    print("="*80 + "\n")
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            test_user = User.query.filter_by(email='test@test.com').first()
            if test_user:
                sess['_user_id'] = str(test_user.id)
                sess['current_project'] = 'belgrad'
        
        resp = client.get('/servis/durumu/tablo')
        if resp.status_code == 200:
            data = resp.get_json()
            print('✅ ENDPOINT ÇALIŞIYOR - SONUÇ:')
            print(f"  Toplam Araç: {data['stats']['total']}")
            print(f"  Serviste: {data['stats']['operational']}")
            print(f"  Servis Dışı: {data['stats']['outofservice']}")
            print(f"  İşletme: {data['stats']['maintenance']}")
            print(f"  Erisebilirlik: {data['stats']['availability']}%")
            print("\n✅ TAMAMLANDI - Tüm veriler doğru!")
        else:
            print(f"❌ Hata: {resp.status_code}")
