#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test KM update POST endpoint directly"""
from app import app
from models import Equipment, db
import json

print("\n" + "="*60)
print("[TEST] KM UPDATE POST ENDPOINT")
print("="*60)

with app.test_client() as client:
    with app.app_context():
        # 1. Login gerekli mi kontrol et
        print("\n[1] GET /tramvay-km (Sayfaya eris):")
        resp = client.get('/tramvay-km')
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 302:
            print("   [NOTE] Login required - redirecting")
        elif resp.status_code == 200:
            print("   [OK] Page accessed")
        
        # 2. Direct POST test et (session ile)
        print("\n[2] POST /tramvay-km/guncelle (Veri guncelle):")
        with client.session_transaction() as sess:
            sess['current_project'] = 'belgrad'
            sess['user_id'] = 1  # Dummy user
        
        update_data = {
            'tram_id': '1531',
            'current_km': '500',
            'notes': 'Test POST update'
        }
        
        resp = client.post('/tramvay-km/guncelle', data=update_data, follow_redirects=False)
        print(f"   Status: {resp.status_code}")
        print(f"   Location: {resp.headers.get('Location', 'N/A')}")
        
        if resp.status_code in [302, 303]:
            print("   [OK] Redirect gerceklesti (basarili)")
        
        # 3. DB'de kontrol et
        print("\n[3] DB'de kontrol et:")
        eq = Equipment.query.filter_by(equipment_code='1531').first()
        if eq:
            print(f"   [OK] Tram 1531 bulundu")
            print(f"   Current KM: {eq.current_km}")
            print(f"   Notes: {eq.notes}")
            if eq.current_km == 500:
                print("   [SUCCESS] KM guncellenmis!")
            else:
                print(f"   [FAIL] KM degismedi: {eq.current_km}")
        
        print("\n" + "="*60)
        print("[OK] TEST TAMAMLANDI")
        print("="*60 + "\n")
