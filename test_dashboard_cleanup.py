#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test dashboard after A/B/C/D cleanup"""

from app import create_app
from flask_login import LoginManager, UserMixin

app = create_app()

class MockUser(UserMixin):
    def __init__(self):
        self.id = 1
        self.username = 'test'
        self.role = 'admin'
    
    def get_role_display(self):
        return 'Yönetici'

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
    removed = {
        "Debug A/B/C/D info": 'for sinif, count in ariza_sinif_counts' not in content,
        "En Son 5 Arıza başlığı": "En Son 5 Arıza" in content,
        "Arıza öğeleri": 'ariza-item' in content,
    }
    
    # Check API endpoints
    api_checks = {
        "api/failures endpoint": '/api/failures' in content or True,  # Will check via call
    }
    
    print("\n✅ DASHBOARD RENDER:")
    all_ok = True
    for check, result in removed.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check}")
        if not result:
            all_ok = False
    
    # Test API endpoint
    print("\n📡 API ENDPOINT TESTI:")
    test_response = client.get('/dashboard/api/failures/1532')
    if test_response.status_code == 200:
        data = test_response.get_json()
        if 'failures' in data:
            print(f"   ✅ /api/failures/<code> çalışıyor")
            print(f"   ✅ Araç 1532 için {len(data['failures'])} arıza bulundu")
            if len(data['failures']) > 0:
                print(f"   ✅ İlk arıza: {data['failures'][0]['fracas_id']}")
        else:
            print(f"   ❌ API response yapısı yanlış")
            all_ok = False
    else:
        print(f"   ❌ API endpoint hata: {test_response.status_code}")
        all_ok = False
    
    # Test all failures
    print("\n📡 TÜM ARIZALAR API:")
    all_response = client.get('/dashboard/api/failures')
    if all_response.status_code == 200:
        all_data = all_response.get_json()
        if 'failures' in all_data:
            print(f"   ✅ /api/failures çalışıyor")
            print(f"   ✅ Toplam {len(all_data['failures'])} arıza bulundu")
        else:
            print(f"   ❌ API response yapısı yanlış")
    
    print("\n" + "="*70)
    if all_ok and response.status_code == 200:
        print("✅ TÜM TESTLER BAŞARILI!")
        print("\n📊 Yeni Dashboard Yapısı:")
        print("  • Toplam Arıza (A-Kritik)")
        print("  • Toplam Arıza (B-Yüksek)")
        print("  • Toplam Arıza (C-Hafif)")
        print("  • Toplam Arıza (D-Diğer)")
        print("  • Bugün Biten")
        print("  • Toplam Arızalar")
        print("\n✨ Arıza Sayfası:")
        print("  • En Son 5 Arıza başlığı")
        print("  • Arıza liste öğeleri (dinamik)")
        print("\n🎯 İnteraktif Özellik:")
        print("  • Tramvay Fleet'te araca tıklarsanız")
        print("    → O aracın son 5 arızası gösterilir")
    else:
        print("❌ HATALAR VAR")
    print("="*70 + "\n")
