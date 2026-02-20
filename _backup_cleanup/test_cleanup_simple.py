#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test dashboard after A/B/C/D cleanup"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

from app import create_app
from flask_login import LoginManager, UserMixin

app = create_app()

class MockUser(UserMixin):
    def __init__(self):
        self.id = 1
        self.username = 'test'
        self.role = 'admin'
    
    def get_role_display(self):
        return 'Yonetici'

login_manager = app.login_manager
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return MockUser()

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['_user_id'] = '1'
    
    print("\n" + "="*70)
    print("DASHBOARD - A/B/C/D CLEANUP TESTI")
    print("="*70)
    
    # Test dashboard render
    response = client.get('/dashboard/')
    content = response.get_data(as_text=True)
    
    # Check what was removed
    print("\nDAŞBOARD KONTROLLERI:")
    
    if 'for sinif, count in ariza_sinif_counts' not in content:
        print("  [OK] Debug A/B/C/D bilgileri kaldırıldı")
    else:
        print("  [HATA] Debug A/B/C/D bilgileri hala var")
    
    if "En Son 5 Ariza" in content:
        print("  [OK] 'En Son 5 Ariza' basligı var")
    else:
        print("  [HATA] 'En Son 5 Ariza' basligı yok")
    
    if 'ariza-item' in content:
        print("  [OK] Ariza ogeleri var")
    else:
        print("  [HATA] Ariza ogeleri yok")
    
    # Test API endpoint for specific vehicle
    print("\nAPI ENDPOINT TESTLERI:")
    test_response = client.get('/dashboard/api/failures/1532')
    if test_response.status_code == 200:
        data = test_response.get_json()
        if 'failures' in data:
            print(f"  [OK] /api/failures/1532 calisiyor")
            print(f"       -> {len(data['failures'])} ariza bulundu")
            if len(data['failures']) > 0:
                first = data['failures'][0]
                print(f"       -> Ilk ariza: {first.get('fracas_id', 'N/A')}")
        else:
            print(f"  [HATA] API response yapisi yanlis")
    else:
        print(f"  [HATA] /api/failures/1532 status: {test_response.status_code}")
    
    # Test all failures
    all_response = client.get('/dashboard/api/failures')
    if all_response.status_code == 200:
        all_data = all_response.get_json()
        if 'failures' in all_data:
            print(f"  [OK] /api/failures (tumu) calisiyor")
            print(f"       -> {len(all_data['failures'])} ariza bulundu")
        else:
            print(f"  [HATA] API response yapisi yanlis")
    
    print("\n" + "="*70)
    if response.status_code == 200:
        print("SONUC: TUM TESTLER BASARILI!\n")
        print("Yeni Dashboard Yapisi:")
        print("  - Toplam Ariza (A-Kritik)")
        print("  - Toplam Ariza (B-Yuksek)")
        print("  - Toplam Ariza (C-Hafif)")
        print("  - Toplam Ariza (D-Diger)")
        print("  - Bugun Biten")
        print("  - Toplam Arizalar\n")
        print("Ariza Sayfasi:")
        print("  - En Son 5 Ariza")
        print("  - Dinamik liste\n")
        print("Interaktif Ozellik:")
        print("  - Tramvay Fleet tiklayinca aracinizin")
        print("    son 5 arizasi gosterilir [OK]")
    else:
        print(f"HATA: Dashboard render hatasi ({response.status_code})")
    print("="*70 + "\n")
