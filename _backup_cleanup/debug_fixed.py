#!/usr/bin/env python3
"""Debug service status page stats - FIXED"""
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
        print(f"SERVICE STATUS PAGE DEBUG (FIXED) - Project: {current_project}")
        print("="*70 + "\n")
        
        # Get tram IDs
        tram_ids = get_tram_ids_from_veriler(current_project)
        print(f"1. Tram IDs from Veriler.xlsx: {len(tram_ids)} trams")
        print(f"   IDs: {tram_ids[:10]}... (first 10)\n")
        
        # Get equipment list
        equipment_list = Equipment.query.filter(
            Equipment.equipment_code.in_(tram_ids),
            Equipment.parent_id == None,
            Equipment.project_code == current_project
        ).all()
        print(f"2. Equipment in DB: {len(equipment_list)} trams\n")
        
        # Calculate stats with FIXED mapping
        tram_status_data = []
        for equipment in equipment_list:
            status_record = ServiceStatus.query.filter_by(
                tram_id=equipment.equipment_code,
                date=today_date,
                project_code=current_project
            ).first()
            
            status_display = 'aktif'
            status_badge = 'Aktif'
            db_status = 'None'
            
            if status_record:
                db_status = status_record.status
                status_value = status_record.status
                
                # CRITICAL: Check "İşletme Kaynaklı" FIRST before "Dışı" 
                # because "İşletme Kaynaklı Servis Dışı" contains both patterns!
                # Use case-insensitive Turkish pattern matching (no lower() to avoid Unicode issues)
                if 'İşletme' in status_value or 'işletme' in status_value:
                    status_display = 'isletme'
                    status_badge = 'İşletme Kaynaklı'
                elif 'Dışı' in status_value or 'dışı' in status_value:
                    status_display = 'ariza'
                    status_badge = 'Servis Dışı'
                elif 'Servis' in status_value or 'servis' in status_value:
                    status_display = 'aktif'
                    status_badge = 'Aktif'
            
            tram_status_data.append({
                'equipment_code': equipment.equipment_code,
                'status': status_display,
                'status_badge': status_badge,
                'db_status': db_status
            })
        
        # Print detailed breakdown
        print(f"3. DETAILED TRAM STATUS BREAKDOWN:")
        for tram in tram_status_data:
            print(f"   {tram['equipment_code']}: DB={tram['db_status']:40} -> status={tram['status']:10} badge={tram['status_badge']}")
        
        # Stats calculation (FIXED)
        servis_disi_count = 0
        isletme_count = 0
        aktif_count = 0
        toplam = len(tram_status_data)
        
        for tram in tram_status_data:
            if tram['status'] == 'ariza':
                servis_disi_count += 1
            elif tram['status'] == 'isletme':
                isletme_count += 1
            elif tram['status'] == 'aktif':
                aktif_count += 1
        
        availability = ((aktif_count) / toplam * 100) if toplam > 0 else 0
        
        stats = {
            'servis_disi': servis_disi_count,
            'isletme': isletme_count,
            'aktif': aktif_count,
            'toplam': toplam,
            'availability': round(availability, 1)
        }
        
        print(f"\n4. STAT CALCULATION (FIXED):")
        print(f"   - Total trams: {toplam}")
        print(f"   - Where status=='aktif': {aktif_count}")
        print(f"   - Where status=='isletme': {isletme_count}")
        print(f"   - Where status=='ariza': {servis_disi_count}")
        print(f"   - availability (aktif/toplam): {availability}%")
        
        print(f"\n5. STATS DICT (what's passed to template):")
        for key, val in stats.items():
            print(f"   {key}: {val}")
        
        print("\n" + "="*70)
        print("✅ EXPECTED MAPPING FOR CORRECT DISPLAY:")
        print("="*70)
        print("  Serviste: stats['aktif'] = " + str(stats['aktif']))
        print("  Servis Dışı: stats['servis_disi'] = " + str(stats['servis_disi']))
        print("  İşletme: stats['isletme'] = " + str(stats['isletme']))
        print("  Toplam: stats['toplam'] = " + str(stats['toplam']))
        print("="*70 + "\n")
