#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Final verification - işletme kaynaklı display"""

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
    
    response = client.get('/dashboard/')
    content = response.get_data(as_text=True)
    
    print("\n" + "="*70)
    print("FINAL VERIFICATION - ISLETME KAYNAKLÎ STATUS")
    print("="*70)
    
    # Look for işletme
    has_isletme_label = 'İşletme Kaynaklı' in content
    has_warning_badge = 'bg-warning' in content
    has_danger_badge = 'bg-danger' in content
    has_success_badge = 'bg-success' in content
    
    print(f"\n[TEMPLATE RENDER CHECKS]")
    print(f"  İşletme Kaynaklı label: {'OK' if has_isletme_label else 'NOT FOUND'}")
    print(f"  bg-warning (turuncu): {'OK' if has_warning_badge else 'NOT FOUND'}")
    print(f"  bg-danger (kirmizi): {'OK' if has_danger_badge else 'MISSING'}")  
    print(f"  bg-success (yesil): {'OK' if has_success_badge else 'MISSING'}")
    
    # Look for status divs
    if 'class="tramvay-card işletme"' in content:
        print(f"  tramvay-card.işletme class: OK")
    elif 'tramvay-card işletme' in content:
        print(f"  tramvay-card işletme: OK")
    else:
        print(f"  tramvay-card işletme: NOT FOUND")
    
    print("\n" + "="*70)
    if has_isletme_label and has_warning_badge:
        print("✅ ISLETME KAYNAKLÎ DURUM BAŞARILI!")
        print("\n   Tramvay Fleet'te İşletme Kaynaklı Servis Dışı araclar:")
        print("   - Turuncu (warning) renkte")
        print("   - 'İşletme Kaynaklı' yazısı gosterilir")
    else:
        print("❌ HATA - İşletme Kaynaklı statüsü düzgün gösterilmiyor")
    print("="*70 + "\n")
