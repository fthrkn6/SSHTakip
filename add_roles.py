"""Rolleri ekle"""
from app import app
from models import db, Role

with app.app_context():
    # Mevcut rolleri sil
    Role.query.delete()
    db.session.commit()
    
    roles_data = [
        ('Admin', 'Sistem yöneticisi - tüm erişim'),
        ('Mühendis', 'Bakım mühendisi - raporlama ve analiz'),
        ('Teknisyen', 'Saha teknisyeni - arıza kaydı'),
    ]
    
    for name, desc in roles_data:
        role = Role(name=name, description=desc, permissions='{}')
        db.session.add(role)
    
    db.session.commit()
    
    roles = Role.query.all()
    print(f'✓ {len(roles)} rol eklendi:')
    for role in roles:
        print(f'  - {role.name}')
