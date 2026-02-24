#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Final KM update test with proper bootstrap"""
from app import app
from models import Equipment, db

print("\n" + "="*70)
print("[FINAL TEST] KM UPDATE WITH BOOTSTRAP FIXED")
print("="*70)

with app.test_client() as client:
    with app.app_context():
        # 1. Baslangic durumu
        print("\n[1] Baslangic - Tram 1531:")
        eq = Equipment.query.filter_by(equipment_code='1531').first()
        before_km = eq.current_km
        print(f"    Current KM: {before_km}")
        
        # 2. Login et
        print("\n[2] Login...")
        login_resp = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        print("   [OK] Logged in")
        
        # 3. /tramvay-km sayfasini kontrol et
        print("\n[3] GET /tramvay-km - sayfa yuksle...")
        page_resp = client.get('/tramvay-km')
        print(f"   Status: {page_resp.status_code}")
        if b'1531' in page_resp.data:
            print("   [OK] Tram 1531 sayfada goruldudu")
        
        # 4. Form gönder
        print("\n[4] POST /tramvay-km/guncelle:")
        test_values = [
            {'km': '5000', 'notes': 'Test 1 - 5000'},
            {'km': '6000', 'notes': 'Test 2 - 6000'},
            {'km': '7000', 'notes': 'Test 3 - 7000'},
        ]
        
        for i, test_data in enumerate(test_values, 1):
            resp = client.post('/tramvay-km/guncelle', data={
                'tram_id': '1531',
                'current_km': test_data['km'],
                'notes': test_data['notes']
            })
            print(f"   [{i}] Status: {resp.status_code}, KM: {test_data['km']}")
        
        # 5. Son deger kontrol et
        print("\n[5] Son Deger (DB):")
        eq2 = Equipment.query.filter_by(equipment_code='1531').first()
        final_km = eq2.current_km
        print(f"    Current KM: {final_km}")
        
        if final_km == 7000:
            print("    [SUCCESS] En son update yazildi!")
        else:
            print(f"    [FAIL] Beklenen 7000 ama {final_km}")
        
        # 6. Excel kontrol et
        print("\n[6] Excel Kontrol:")
        import pandas as pd
        import os
        xl_file = os.path.join('data', 'belgrad', 'km_data.xlsx')
        if os.path.exists(xl_file):
            df = pd.read_excel(xl_file)
            tram_row = df[df['tram_id'].astype(str) == '1531']
            if not tram_row.empty:
                excel_km = tram_row.iloc[0]['current_km']
                notes_text = tram_row.iloc[0]['notes']
                print(f"    Excel KM: {excel_km}")
                print(f"    Excel Notes: {notes_text}")
                if excel_km == 7000:
                    print("    [SUCCESS] Excel da guencellenmis!")
                else:
                    print(f"    [FAIL] Excel'de {excel_km}")
        
        print("\n" + "="*70)
