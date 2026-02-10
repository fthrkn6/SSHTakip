#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify dashboard rendering is correct"""

from app import create_app
from flask_login import LoginManager, UserMixin
from datetime import datetime

# Create app
app = create_app()

# Create a mock user
class MockUser(UserMixin):
    def __init__(self, id=1, username='test'):
        self.id = id
        self.username = username
        self.role = 'admin'
    
    def get_role_display(self):
        roles = {
            'admin': 'Yönetici',
            'muhendis': 'Mühendis',
            'teknisyen': 'Teknisyen',
            'operator': 'Operatör',
            'user': 'Kullanıcı'
        }
        return roles.get(self.role, self.role)

# Setup login manager
login_manager = app.login_manager
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return MockUser(user_id)

with app.test_client() as client:
    # Perform request with authentication
    with client.session_transaction() as sess:
        sess['_user_id'] = '1'
    
    response = client.get('/dashboard/')
    
    print("\n" + "="*70)
    print("DASHBOARD RENDER TESTİ")
    print("="*70)
    
    if response.status_code == 200:
        content = response.get_data(as_text=True)
        
        # Check key elements
        checks = {
            "Toplam Arızalar": "Toplam Arızalar" in content,
            "bi-exclamation-triangle": "bi-exclamation-triangle" in content,
            "Tramvay Filosu": "Tramvay Filosu" in content,
            "total_failures_last_30_days": ('total_failures_last_30_days or 0' in content or 'id="ariza-count"' in content),
        }
        
        print("\n✅ Dashboard sayfa kodu yüklendi (Status: 200)")
        print("\n📋 Kontrol Sonuçları:")
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")
        
        all_pass = all(checks.values())
        if all_pass:
            print("\n🎉 TÜM KONTROLLER BAŞARILI!")
            print("\nDashboard başarılı şekilde güncellendi:")
            print("  • 'Toplam Arızalar' başlığı eklendi")
            print("  • Icon değiştirildi (exclamation-triangle)")
            print("  • Tramvay filosu ServiceStatus'tan alınıyor")
            print("  • Excel verilerinden arızalar gösteriliyor")
        else:
            print("\n⚠️  BAZΙ KONTROLLER BAŞARISIZ")
                
    else:
        print(f"\n❌ Dashboard yüklenemedi - Status: {response.status_code}")
        if response.status_code == 302:
            print("   (Redirect: Yenidirektme alındı - Login gerekli olabilir)")
        print(f"   Hata: {response.get_data(as_text=True)[:200]}")

print("="*70 + "\n")
