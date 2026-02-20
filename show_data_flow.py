#!/usr/bin/env python3
"""Complete data flow visualization"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import User, ServiceStatus, Equipment
from datetime import date

app = create_app()
with app.app_context():
    today = str(date.today())
    
    print("\n" + "="*80)
    print("COMPLETE DATA FLOW ANALYSIS")
    print("="*80)
    
    print("\n1️⃣  DATABASE - ServiceStatus RECORDS (Today)")
    print("-" * 80)
    
    for project in ['belgrad', 'kayseri']:
        records = ServiceStatus.query.filter_by(project_code=project, date=today).order_by(ServiceStatus.tram_id).all()
        print(f"\n{project.upper()} ({len(records)} records):")
        
        status_breakdown = {}
        for rec in records[:3]:  # Show first 3 as sample
            status_breakdown[rec.status] = status_breakdown.get(rec.status, 0) + 1
            print(f"  {rec.tram_id}: {rec.status}")
        print(f"  ... ({len(records)-3} more records)")
        
        # Count all
        all_status_breakdown = {}
        for rec in records:
            all_status_breakdown[rec.status] = all_status_breakdown.get(rec.status, 0) + 1
        
        print(f"\nStatus Summary for {project.upper()}:")
        for status, count in sorted(all_status_breakdown.items()):
            print(f"  - {status}: {count}")
    
    print("\n" + "="*80)
    print("2️⃣  BACKEND - Stats Calculation (routes/service_status.py)")
    print("-" * 80)
    
    # Simulate stats calculation for belgrad
    equipment_list = Equipment.query.filter_by(project_code='belgrad', parent_id=None).all()
    aktif = 0
    servis_disi = 0
    isletme = 0
    
    for eq in equipment_list:
        rec = ServiceStatus.query.filter_by(
            tram_id=eq.equipment_code,
            date=today,
            project_code='belgrad'
        ).first()
        
        if rec:
            status_val = rec.status
            if 'İşletme' in status_val or 'işletme' in status_val:
                isletme += 1
            elif 'Dışı' in status_val or 'dışı' in status_val:
                servis_disi += 1
            elif 'Servis' in status_val or 'servis' in status_val:
                aktif += 1
    
    print(f"\nBelgrad Stats Dict (passed to template):")
    print(f"  stats['aktif']: {aktif}")
    print(f"  stats['servis_disi']: {servis_disi}")
    print(f"  stats['isletme']: {isletme}")
    print(f"  stats['toplam']: {len(equipment_list)}")
    print(f"  stats['availability']: {round(aktif/len(equipment_list)*100, 1)}%")
    
    print("\n" + "="*80)
    print("3️⃣  TEMPLATE RENDERING & JAVASCRIPT")
    print("-" * 80)
    
    print(f"\nservis_durumu_enhanced.html:")
    print(f"  ✅ Page load: Cards show 0 (boş başlangıç)")
    print(f"  ✅ JS fetch /servis/durumu/tablo endpoint")
    print(f"  ✅ Endpoint returns stats dict")
    print(f"  ✅ JS updates cards with real values:")
    print(f"      - Serviste: {aktif}")
    print(f"      - Servis Dışı: {servis_disi}")
    print(f"      - İşletme: {isletme}")
    print(f"      - Toplam: {len(equipment_list)}")
    print(f"      - Availability: {round(aktif/len(equipment_list)*100, 1)}%")
    
    print("\n" + "="*80)
    print("4️⃣  DATA SOURCES PER PROJECT")
    print("-" * 80)
    
    for project in ['belgrad', 'kayseri']:
        equip = Equipment.query.filter_by(project_code=project, parent_id=None).count()
        ss = ServiceStatus.query.filter_by(project_code=project, date=today).count()
        print(f"\n{project.upper()}:")
        print(f"  - Equipment table: {equip} tramvay")
        print(f"  - ServiceStatus (today): {ss} records")
        print(f"  - Source (tram_id list): data/{project}/Veriler.xlsx Sayfa2")
    
    print("\n" + "="*80 + "\n")
