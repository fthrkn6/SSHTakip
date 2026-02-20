#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test tramvay ve ekipman verisi ekle"""

from app import create_app, db
from models import Equipment

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("📝 TEST VERİSİ EKLENIYOR...")
    print("="*60)
    
    # Belgrad tramvayları
    belgrad_trams = [
        ('1531', 'Tramvay 1531', 'aktif'),
        ('1532', 'Tramvay 1532', 'aktif'),
        ('1533', 'Tramvay 1533', 'işletme'),
        ('1534', 'Tramvay 1534', 'aktif'),
        ('1535', 'Tramvay 1535', 'ariza'),
        ('1536', 'Tramvay 1536', 'aktif'),
        ('1537', 'Tramvay 1537', 'aktif'),
        ('1538', 'Tramvay 1538', 'aktif'),
    ]
    
    # Kayseri tramvayları
    kayseri_trams = [
        ('KAY01', 'Kayseri 01', 'aktif'),
        ('KAY02', 'Kayseri 02', 'aktif'),
        ('KAY03', 'Kayseri 03', 'işletme'),
        ('KAY04', 'Kayseri 04', 'aktif'),
        ('KAY05', 'Kayseri 05', 'aktif'),
        ('KAY06', 'Kayseri 06', 'ariza'),
        ('KAY07', 'Kayseri 07', 'aktif'),
        ('KAY08', 'Kayseri 08', 'aktif'),
        ('KAY09', 'Kayseri 09', 'aktif'),
        ('KAY10', 'Kayseri 10', 'aktif'),
    ]
    
    # Belgrad ekipmanlarını ekle
    print("\n🚊 BELGRAD TRAMVAYLARI ekleniyor...")
    for code, name, status in belgrad_trams:
        existing = Equipment.query.filter_by(equipment_code=code).first()
        if not existing:
            eq = Equipment(
                equipment_code=code,
                name=name,
                equipment_type='Tramway',
                status=status,
                project_code='belgrad',
                location='Belgrad',
                criticality='high'
            )
            db.session.add(eq)
            print(f"  ✓ {code}: {name} ({status})")
    
    # Kayseri ekipmanlarını ekle
    print("\n🚊 KAYSERI TRAMVAYLARI ekleniyor...")
    for code, name, status in kayseri_trams:
        existing = Equipment.query.filter_by(equipment_code=code).first()
        if not existing:
            eq = Equipment(
                equipment_code=code,
                name=name,
                equipment_type='Tramway',
                status=status,
                project_code='kayseri',
                location='Kayseri',
                criticality='high'
            )
            db.session.add(eq)
            print(f"  ✓ {code}: {name} ({status})")
    
    db.session.commit()
    print("\n" + "="*60)
    print("✅ Test verisi başarıyla eklendi!")
    print("="*60 + "\n")
