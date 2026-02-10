#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug status_display value"""

from app import create_app
from models import db, Equipment, ServiceStatus
from datetime import date

app = create_app()

with app.app_context():
    print("\n" + "="*70)
    print("DASHBOARD DATA DEBUG")
    print("="*70)
    
    tramvaylar = Equipment.query.filter_by(parent_id=None).all()
    today = str(date.today())
    
    print(f"\nGun: {today}")
    print(f"Arac Sayisi: {len(tramvaylar)}")
    
    for tramvay in tramvaylar:
        status_record = ServiceStatus.query.filter_by(
            tram_id=tramvay.equipment_code,
            date=today
        ).first()
        
        if status_record:
            status_value = status_record.status if status_record.status else 'Servis'
            status_lower = status_value.lower()
            
            # Determine status
            if 'işletme kaynaklı' in status_lower or 'isletme aynaklı' in status_lower or 'işletme' in status_lower:
                status_display = 'işletme'
            elif 'servis dışı' in status_lower or 'servis disi' in status_lower or 'dışı' in status_lower:
                status_display = 'ariza'
            else:
                status_display = 'aktif'
            
            if status_display != 'aktif':
                print(f"\nArac {tramvay.equipment_code}:")
                print(f"  DB: '{status_value}'")
                print(f"  Lower: '{status_lower}'")
                print(f"  Display: '{status_display}'")
                print(f"  Has 'işletme': {'işletme' in status_lower}")
                print(f"  Has 'dışı': {'dışı' in status_lower}")
    
    print("\n" + "="*70 + "\n")
