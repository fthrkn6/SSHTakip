#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test: ServiceStatus'ten veri oku"""

from app import create_app, db
from models import Equipment, ServiceStatus
from datetime import date

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("📊 SERVICE STATUS -> DASHBOARD TEST")
    print("="*60)
    
    today = str(date.today())
    
    # Test 1: Kayseri için bugünün ServiceStatus kaydını ekle
    print(f"\n📝 {today} tarihinde Kayseri tramvayları için ServiceStatus ekle:")
    
    kayseri_trams = ['KAY01', 'KAY02', 'KAY03', 'KAY04', 'KAY05', 
                     'KAY06', 'KAY07', 'KAY08', 'KAY09', 'KAY10']
    
    # Eski kayıtları sil
    ServiceStatus.query.filter_by(project_code='kayseri', date=today).delete()
    
    # Yeni kayıtlar ekle
    statuses = ['Servis', 'Servis', 'İşletme Kaynaklı Servis Dışı', 'Servis', 'Servis',
                'Servis Dışı', 'Servis', 'Servis', 'Servis', 'Servis']
    
    for tram_id, status in zip(kayseri_trams, statuses):
        record = ServiceStatus(
            tram_id=tram_id,
            date=today,
            status=status,
            project_code='kayseri'
        )
        db.session.add(record)
        print(f"  ✓ {tram_id}: {status}")
    
    db.session.commit()
    
    # Test 2: Stats hesaplaması
    print(f"\n📊 Kayseri'nin DASHBOARD STATS (ServiceStatus'ten):")
    
    equipment_list = Equipment.query.filter_by(project_code='kayseri', parent_id=None).all()
    
    aktif = 0
    isletme = 0
    ariza = 0
    
    for eq in equipment_list:
        service = ServiceStatus.query.filter_by(
            tram_id=eq.equipment_code,
            date=today,
            project_code='kayseri'
        ).first()
        
        if service:
            if 'İşletme' in service.status:
                isletme += 1
                print(f"  {eq.equipment_code}: İŞLETME")
            elif 'Dışı' in service.status:
                ariza += 1
                print(f"  {eq.equipment_code}: ARIZA")
            else:
                aktif += 1
                print(f"  {eq.equipment_code}: AKTİF")
        else:
            aktif += 1
            print(f"  {eq.equipment_code}: AKTİF (default)")
    
    total = len(equipment_list)
    availability = ((aktif + isletme) / total * 100) if total > 0 else 0
    
    print(f"\n  Toplam: {total}")
    print(f"  Aktif: {aktif}")
    print(f"  İşletme: {isletme}")
    print(f"  Arıza: {ariza}")
    print(f"  Filo Emre Amadelik: {availability:.1f}%")
    
    print("\n" + "="*60)
