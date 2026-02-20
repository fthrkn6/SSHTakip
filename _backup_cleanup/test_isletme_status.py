#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test işletme kaynaklı statüsü"""

from app import create_app
from models import db, ServiceStatus, Equipment
from datetime import date
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

print("\n" + "="*70)
print("ISLETME KAYNAKLÎ STATU KONTROLU")
print("="*70)

with app.app_context():
    # Araç 1538 İşletme Kaynaklı Servis Dışı olmalı
    status_1538 = ServiceStatus.query.filter_by(
        tram_id='1538',
        date=str(date.today())
    ).first()
    
    status_1531 = ServiceStatus.query.filter_by(
        tram_id='1531',
        date=str(date.today())
    ).first()
    
    print(f"\nArac 1538 Statüsü:")
    if status_1538:
        print(f"  DB Degeri: '{status_1538.status}'")
        print(f"  'isletme kaynaklı' içeriyor: {'işletme kaynaklı' in status_1538.status.lower()}")
    else:
        print(f"  BULUNAMADI")
    
    print(f"\nArac 1531 Statüsü:")
    if status_1531:
        print(f"  DB Degeri: '{status_1531.status}'")
        print(f"  'servis disi' içeriyor: {'servis dışı' in status_1531.status.lower()}")
    else:
        print(f"  BULUNAMADI")

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['_user_id'] = '1'
    
    response = client.get('/dashboard/')
    content = response.get_data(as_text=True)
    
    print(f"\nDASHBOARD TEMPLATE CIKTISI:")
    
    # Check for işletme kaynaklı
    if 'İşletme Kaynaklı' in content:
        print(f"  [OK] 'İşletme Kaynaklı' labels var")
    else:
        print(f"  [HATA] 'İşletme Kaynaklı' labels yok")
    
    # Check for orange/warning color class
    if 'tramvay-card.işletme' in content or 'bg-warning' in content:
        print(f"  [OK] Turuncu renk (warning) CSS var")
    else:
        print(f"  [HATA] Turuncu renk CSS yok")
    
    # Check for tramvay-card.işletme class
    if 'class="tramvay-card işletme"' in content or 'tramvay-card işletme' in content or 'tramvay-card.işletme' in content:
        print(f"  [OK] tramvay-card.işletme class kullanılıyor")
    else:
        print(f"  [HATA] tramvay-card.işletme class kullanılmıyor")

print("\n" + "="*70 + "\n")
