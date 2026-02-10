#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify ariza sınıfı metrics render correctly"""

from app import create_app
from flask_login import LoginManager, UserMixin

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
    # Setup authentication
    with client.session_transaction() as sess:
        sess['_user_id'] = '1'
    
    response = client.get('/dashboard/')
    
    print("\n" + "="*80)
    print("ARIZA SINIFI METRİK KARTLARI TESTİ")
    print("="*80)
    
    if response.status_code == 200:
        content = response.get_data(as_text=True)
        
        # Check for ariza class metrics
        checks = {
            "A-Kritik": "A-Kritik" in content,
            "B-Yüksek": "B-Yüksek" in content,
            "C-Hafif": "C-Hafif" in content,
            "D-Diğer": "D-Diğer" in content,
            "Toplam Arıza": "Toplam Arıza" in content,
            "ariza_sinif_counts": ("ariza_sinif_counts" in content or "metric-value" in content),
        }
        
        print("\n✅ Dashboard yüklendi (Status: 200)")
        print("\n📋 Arıza Sınıfı Kontrolleri:")
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")
        
        all_pass = all(checks.values())
        if all_pass:
            print("\n🎉 ARİZA SINIFI METRİKLERİ BAŞARILI!")
            print("\nDashboard'da gösterilen kartlar:")
            print("  • Toplam Arıza (A-Kritik/Emniyet Riski)")
            print("  • Toplam Arıza (B-Yüksek/Operasyon Engeller)")
            print("  • Toplam Arıza (C-Hafif/Kısıtlı Operasyon)")
            print("  • Toplam Arıza (D-Arıza Değildir)")
            
            # Find and display metric values from HTML
            import re
            # Try to find metric values
            pattern = r'<div class="metric-value[^"]*>(\d+)</div>'
            matches = re.findall(pattern, content)
            if matches:
                print(f"\n📊 İlk 4 metrik değeri: {matches[:4]}")
        else:
            print("\n⚠️ BAZΙ KONTROLLER BAŞARISIZ")
            # Show snippet of HTML to debug
            if "Toplam Arıza" in content:
                idx = content.find("Toplam Arıza")
                print(f"\n🔍 HTML snippet:\n{content[max(0, idx-100):idx+200]}")
    else:
        print(f"\n❌ Dashboard yüklenemedi - Status: {response.status_code}")

print("\n" + "="*80 + "\n")
