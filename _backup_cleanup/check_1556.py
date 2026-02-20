#!/usr/bin/env python3
"""Check - All routes show 1556?"""
import sys
sys.path.insert(0, '.')

from app import create_app
from models import Equipment, ServiceStatus
from datetime import date
import pandas as pd
import os

app = create_app()

with app.app_context():
    project = 'belgrad'
    today = str(date.today())
    
    print("\n" + "="*100)
    print("FINAL CHECK - All routes showing 1556?")
    print("="*100 + "\n")
    
    # 1. Excel
    veriler_path = os.path.join(app.root_path, 'data', project, 'Veriler.xlsx')
    df = pd.read_excel(veriler_path, sheet_name='Sayfa2', header=0)
    excel_trams = sorted([str(t) for t in df['tram_id'].dropna().unique().tolist()])
    
    print(f"EXCEL: {len(excel_trams)} vehicles")
    print(f"  1556 present? {'YES' if '1556' in excel_trams else 'NO'}\n")
    
    # 2. Dashboard
    equipment_list = Equipment.query.filter_by(
        project_code=project,
        parent_id=None
    ).order_by(Equipment.equipment_code).all()
    
    equipment_trams = sorted([eq.equipment_code for eq in equipment_list])
    print(f"DASHBOARD (Equipment): {len(equipment_trams)} vehicles")
    print(f"  1556 present? {'YES' if '1556' in equipment_trams else 'NO'}\n")
    
    # 3. Service Status
    status_records = ServiceStatus.query.filter_by(
        date=today,
        project_code=project
    ).order_by(ServiceStatus.tram_id).all()
    
    status_trams = sorted(list(set([ss.tram_id for ss in status_records])))
    print(f"SERVICE STATUS: {len(status_trams)} vehicles")
    print(f"  1556 present? {'YES' if '1556' in status_trams else 'NO'}\n")
    
    # 4. Maintenance
    from routes.maintenance import load_trams_from_file
    maintenance_trams = sorted(load_trams_from_file(project))
    print(f"MAINTENANCE (load_trams_from_file): {len(maintenance_trams)} vehicles")
    print(f"  1556 present? {'YES' if '1556' in maintenance_trams else 'NO'}\n")
    
    # Summary
    print("="*100)
    print("SUMMARY")
    print("="*100)
    
    checks = {
        'Dashboard': '1556' in equipment_trams,
        'Service Status': '1556' in status_trams,
        'Maintenance Plans': '1556' in maintenance_trams,
        'Reports': '1556' in maintenance_trams,
    }
    
    all_pass = all(checks.values())
    
    for name, result in checks.items():
        status = '[PASS]' if result else '[FAIL]'
        print(f"{status} {name}: {'VISIBLE' if result else 'HIDDEN'}")
    
    print("\n" + "="*100)
    if all_pass:
        print("SUCCESS: All routes showing 1556 - PROBLEM SOLVED!")
    else:
        print("PROBLEM: Some routes not showing 1556")
    print("="*100 + "\n")
