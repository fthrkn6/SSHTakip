#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test KM update with proper login"""
from app import app
from models import User, Equipment, db

print("\n" + "="*60)
print("[TEST] KM UPDATE WITH PROPER LOGIN")
print("="*60)

with app.test_client() as client:
    with app.app_context():
        # 1. User var mi kontrol et
        print("\n[1] User Kontrol:")
        user = User.query.first()
        if user:
            print(f"   [OK] User bulundu: {user.username}")
        else:
            print("   [ERROR] User yok!")
        
        # 2. Login yap
        print("\n[2] Login Yap:")
        login_resp = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        print(f"   Status: {login_resp.status_code}")
        
        if login_resp.status_code == 200 and 'dashboard' in login_resp.request.path:
            print("   [OK] Login basarili")
        else:
            print(f"   [NOTE] Response path: {login_resp.request.path}")
        
        # 3. GET tramvay-km page
        print("\n[3] GET /tramvay-km:")
        page_resp = client.get('/tramvay-km')
        print(f"   Status: {page_resp.status_code}")
        
        # 4. POST guncelle with login
        print("\n[4] POST /tramvay-km/guncelle (with login):")
        update_data = {
            'tram_id': '1531',
            'current_km': '600',
            'notes': 'Oturum ile test'
        }
        
        update_resp = client.post('/tramvay-km/guncelle', data=update_data, follow_redirects=False)
        print(f"   Status: {update_resp.status_code}")
        print(f"   Location: {update_resp.headers.get('Location', 'N/A')}")
        
        # 5. Check DB
        print("\n[5] DB'de Sonuc:")
        eq = Equipment.query.filter_by(equipment_code='1531').first()
        if eq:
            print(f"   Current KM: {eq.current_km}")
            if eq.current_km == 600:
                print("   [SUCCESS] KM guncellendi!")
            else:
                print(f"   [FAIL] KM guncellenmedi")
        
        print("\n" + "="*60)
        print("[OK] TEST TAMAMLANDI")
        print("="*60 + "\n")
