#!/usr/bin/env python
"""
Sync Istanbul and Samsun km_data.xlsx to Equipment table
"""
import sys
sys.path.insert(0, r'c:\Users\fatiherkin\Desktop\bozankaya_ssh_takip')

from app import app, db
from utils_project_excel_store import sync_km_excel_to_equipment
from models import Equipment

with app.app_context():
    print("="*60)
    print("SYNCING KM DATA TO EQUIPMENT TABLE")
    print("="*60)
    
    print("\nSyncing Istanbul km_data.xlsx to Equipment table...")
    istanbul_count = sync_km_excel_to_equipment('istanbul')
    print(f"✓ Istanbul: {istanbul_count} equipment records created/updated")
    
    print("\nSyncing Samsun km_data.xlsx to Equipment table...")
    samsun_count = sync_km_excel_to_equipment('samsun')
    print(f"✓ Samsun: {samsun_count} equipment records created/updated")
    
    # Verify
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    istanbul_equip = Equipment.query.filter_by(project_code='istanbul').all()
    print(f"\nIstanbul equipment count: {len(istanbul_equip)}")
    if istanbul_equip:
        codes = [eq.equipment_code for eq in istanbul_equip]
        print(f"  Equipment codes: {codes}")
    
    samsun_equip = Equipment.query.filter_by(project_code='samsun').all()
    print(f"\nSamsun equipment count: {len(samsun_equip)}")
    if samsun_equip:
        codes = [eq.equipment_code for eq in samsun_equip]
        print(f"  Equipment codes: {codes}")
    
    print("\n" + "="*60)
    print("✓ SYNC COMPLETED SUCCESSFULLY!")
    print("="*60)
