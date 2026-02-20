#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dashboard stats debug scripti"""

from app import create_app, db
from models import Equipment, ServiceStatus
from datetime import date

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("📊 DASHBOARD STATS DEBUG")
    print("="*60)
    
    # Test 1: Equipment verileri
    print("\n1️⃣  EQUIPMENT VERİLERİ")
    for project in ['belgrad', 'kayseri']:
        count = Equipment.query.filter_by(project_code=project, parent_id=None).count()
        status_dist = db.session.query(
            Equipment.status, 
            db.func.count(Equipment.id)
        ).filter_by(project_code=project, parent_id=None).group_by(Equipment.status).all()
        
        print(f"\n📍 {project.upper()}:")
        print(f"  Toplam tramvay: {count}")
        print(f"  Status dağılımı:")
        for status, cnt in status_dist:
            print(f"    - {status}: {cnt}")
    
    # Test 2: ServiceStatus verileri
    print("\n2️⃣  SERVICE STATUS VERİLERİ")
    today = str(date.today())
    for project in ['belgrad', 'kayseri']:
        count = ServiceStatus.query.filter_by(project_code=project, date=today).count()
        print(f"  {project}: {count} kayıt (bugün)")
    
    # Test 3: Stats hesaplama
    print("\n3️⃣  STATS HESAPLAMA TESTİ (Kayseri)")
    project = 'kayseri'
    
    trams = Equipment.query.filter_by(project_code=project, parent_id=None).all()
    print(f"\n  Tramvay sayısı: {len(trams)}")
    
    if trams:
        aktif = sum(1 for t in trams if t.status and t.status.lower() in ['aktif'])
        isletme = sum(1 for t in trams if t.status and t.status.lower() in ['bakim', 'isletme', 'işletme'])
        ariza = sum(1 for t in trams if t.status and t.status.lower() in ['ariza', 'servis_disi', 'disi'])
        
        print(f"  Aktif: {aktif}")
        print(f"  İşletme: {isletme}")
        print(f"  Arıza: {ariza}")
        
        total = len(trams)
        availability = ((aktif + isletme) / total * 100) if total > 0 else 0
        print(f"\n  ✅ FLEET AVAILABILITY: {availability:.1f}%")
    else:
        print("  ❌ Tramvay yok!")
        
    print("\n" + "="*60)
