#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Default roller oluşturma script'i"""

from app import app, db
from models import Role

app.app_context().push()

# Default rolleri kontrol et ve oluştur - SADECE 3 TEMEL ROL
default_roles = [
    {'name': 'Admin', 'description': 'Sistem yöneticisi - tüm erişim'},
    {'name': 'Mühendis', 'description': 'Bakım mühendisi - raporlama ve analiz'},
    {'name': 'Teknisyen', 'description': 'Saha teknisyeni - arıza kaydı'},
]

existing_roles = {r.name for r in Role.query.all()}

for role_data in default_roles:
    if role_data['name'] not in existing_roles:
        role = Role(name=role_data['name'], description=role_data['description'])
        db.session.add(role)
        print(f"✓ Oluşturuldu: {role_data['name']}")
    else:
        print(f"✗ Zaten var: {role_data['name']}")

db.session.commit()

# Doğrulama
roles = Role.query.all()
print(f"\n📊 Toplam rol: {len(roles)}")
for r in roles:
    print(f"  {r.id}: {r.name} - {r.description}")
