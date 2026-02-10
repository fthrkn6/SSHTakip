#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test the updated metrics layout"""

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
    
    response = client.get('/dashboard/')
    content = response.get_data(as_text=True)
    
    print("\n" + "="*70)
    print("METRİK KARTLARI TESTİ")
    print("="*70)
    
    # Should show
    should_show = {
        "Toplam Arıza (A-Kritik)": "A-Kritik" in content,
        "Toplam Arıza (B-Yüksek)": "B-Yüksek" in content,
        "Toplam Arıza (C-Hafif)": "C-Hafif" in content,
        "Toplam Arıza (D-Diğer)": "D-Diğer" in content,
        "Bugün Biten": "Bugün Biten" in content,
        "Toplam Arızalar": "Toplam Arızalar" in content,
    }
    
    # Should NOT show
    should_not_show = {
        "Bekleyen İş": "Bekleyen İş" in content,
        "Devam Eden": "Devam Eden" in content,
        "Kritik Arıza": "Kritik Arıza" in content,
        "Aylık Maliyet": "Aylık Maliyet" in content,
    }
    
    print("\n✅ GÖSTERİLMESİ GEREKEN:")
    all_ok = True
    for metric, exists in should_show.items():
        status = "✅" if exists else "❌"
        print(f"   {status} {metric}")
        if not exists:
            all_ok = False
    
    print("\n❌ GÖSTERİLMEMESİ GEREKEN:")
    for metric, exists in should_not_show.items():
        status = "✅" if not exists else "❌"
        print(f"   {status} {metric} (var: {exists})")
        if exists:
            all_ok = False
    
    print("\n" + "="*70)
    if all_ok and response.status_code == 200:
        print("✅ TÜM TESTLER BAŞARILI!")
        print("\nGösterilen kartlar:")
        print("  • Toplam Arıza (A-Kritik)")
        print("  • Toplam Arıza (B-Yüksek)")
        print("  • Toplam Arıza (C-Hafif)")
        print("  • Toplam Arıza (D-Diğer)")
        print("  • Bugün Biten")
        print("  • Toplam Arızalar")
    else:
        print("❌ HATALAR VAR - Lütfen kontrol ediniz")
    print("="*70 + "\n")
