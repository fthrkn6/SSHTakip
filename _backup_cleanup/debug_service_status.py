#!/usr/bin/env python3
"""Debug service status page stats"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment, ServiceStatus
from routes.service_status import get_tram_ids_from_veriler
from datetime import date

app = create_app()
with app.app_context():
    with app.test_request_context():
        from flask import session
        session['current_project'] = 'belgrad'
        
        current_project = 'belgrad'
        today_date = str(date.today())
        
        print("\n" + "="*70)
        print(f"SERVICE STATUS PAGE DEBUG - Project: {current_project}")
        print("="*70 + "\n")
        
        # Get tram IDs
        tram_ids = get_tram_ids_from_veriler(current_project)
        print(f"1. Tram IDs from Veriler.xlsx: {len(tram_ids)} trams")
        print(f"   IDs: {tram_ids}\n")
        
        # Get equipment list
        equipment_list = Equipment.query.filter(
            Equipment.equipment_code.in_(tram_ids),
            Equipment.parent_id == None,
            Equipment.project_code == current_project
        ).all()
        print(f"2. Equipment in DB: {len(equipment_list)} trams\n")
        
        # Calculate stats
        tram_status_data = []
        for equipment in equipment_list:
            status_record = ServiceStatus.query.filter_by(
                tram_id=equipment.equipment_code,
                date=today_date,
                project_code=current_project
            ).first()
            
            status_display = 'aktif'
            status_badge = 'Aktif'
            
            if status_record:
                status_value = status_record.status.lower()
                
                # CRITICAL: Check "işletme kaynaklı" FIRST before "servis dışı" 
                # because "işletme kaynaklı servis dışı" contains both!
                if 'işletme kaynaklı' in status_value:
                    status_display = 'isletme'
                    status_badge = 'İşletme Kaynaklı'
                elif 'servis dışı' in status_value:
                    status_display = 'ariza'
                    status_badge = 'Servis Dışı'
                elif 'servis' in status_value:
                    status_display = 'aktif'
                    status_badge = 'Aktif'
            
            tram_status_data.append({
                'equipment_code': equipment.equipment_code,
                'status': status_display,
                'status_badge': status_badge
            })
        
        # Stats calculation
        servis_disi_count = 0
        isletme_count = 0
        toplam = len(tram_status_data)
        
        print(f"4. DETAILED TRAM STATUS BREAKDOWN:")
        for tram in tram_status_data:
            status = tram['status']
            badge = tram['status_badge']
            print(f"   {tram['equipment_code']}: status={status}, badge={badge}")
            
            if tram['status'] == 'ariza':
                servis_disi_count += 1
            elif tram['status_badge'] == 'İşletme Kaynaklı':
                isletme_count += 1
        
        aktif_count = toplam - servis_disi_count
        availability = ((aktif_count) / toplam * 100) if toplam > 0 else 0
        
        print(f"\n5. STAT CALCULATION LOGIC:")
        print(f"   - Total trams: {toplam}")
        print(f"   - Where status=='ariza': {servis_disi_count} (Servis Dişı)")
        print(f"   - Where badge=='İşletme Kaynaklı': {isletme_count} (İşletme)")
        print(f"   - aktif_count (toplam - servis_disi): {aktif_count}")
        
        stats = {
            'servis_disi': servis_disi_count,
            'isletme': isletme_count,
            'aktif': aktif_count,
            'toplam': toplam,
            'availability': round(availability, 1)
        }
        
        print(f"3. STATS DICT (what's passed to template):")
        for key, val in stats.items():
            print(f"   {key}: {val}")
        
        print(f"\n4. Breakdown by status:")
        status_breakdown = {}
        for tram in tram_status_data:
            badge = tram['status_badge']
            status_breakdown[badge] = status_breakdown.get(badge, 0) + 1
        for badge, count in sorted(status_breakdown.items()):
            print(f"   {badge}: {count}")
        
        print("\n" + "="*70)
        print("EXPECTED TEMPLATE KEYS")
        print("="*70)
        print("Template should use stats['servis_disi'], stats['isletme'], etc")
        print("But some templates may expect: stats['Servis'], stats['Servis Dışı'], etc")
        print("\nFIX: Update template keys in servis_durumu_enhanced.html!")
        print("="*70 + "\n")
