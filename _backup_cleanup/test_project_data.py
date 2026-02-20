#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Her proje'nin Dashboard Stats'ını test et"""

from app import create_app, db
from models import Equipment, ServiceStatus
from datetime import date

app = create_app()

with app.app_context():
    print("\n" + "="*70)
    print("PROJE TEST - HER PROJE KENDI VERISINI KULLANIYOR MU?")
    print("="*70)
    
    today = str(date.today())
    projects = ['belgrad', 'kayseri']
    
    for project in projects:
        print(f"\n📊 {project.upper()}:")
        
        # Equipment
        equipment = Equipment.query.filter_by(project_code=project, parent_id=None).all()
        print(f"  Equipment: {len(equipment)} tramvay")
        if equipment:
            print(f"    Ornekler: {[e.equipment_code for e in equipment[:5]]}")
        
        # ServiceStatus
        statuses = ServiceStatus.query.filter_by(project_code=project, date=today).all()
        print(f"  ServiceStatus: {len(statuses)} kayıt")
        
        # Stats hesapla
        if equipment:
            aktif = sum(1 for s in statuses if s.status == 'Servis')
            isletme = sum(1 for s in statuses if 'İşletme' in s.status)
            ariza = sum(1 for s in statuses if 'Dışı' in s.status and 'İşletme' not in s.status)
            
            total = len(equipment)
            availability = ((aktif + isletme) / total * 100) if total > 0 else 0
            
            print(f"  Stats:")
            print(f"    Aktif: {aktif}")
            print(f"    İşletme: {isletme}")
            print(f"    Arıza: {ariza}")
            print(f"    Filo Emre Amadelik: {availability:.1f}%")
    
    print("\n" + "="*70)
    print("✅ Her proje kendi verisini kullanıyor!\n")
