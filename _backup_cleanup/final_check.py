#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KONTROL - Tüm route'lar 1556'yı gösteriyor mu?"""
import sys
sys.path.insert(0, '.')

from app import create_app
from models import Equipment, ServiceStatus, MaintenancePlan
from datetime import date
import pandas as pd
import os

app = create_app()

with app.app_context():
    project = 'belgrad'
    today = str(date.today())
    
    print("\n" + "="*100)
    print("[CHECK] Tumun route lar 1556 yi gosteriyor mu?")
    print("="*100 + "\n")
    
    # 1. Excel'den oku
    veriler_path = os.path.join(app.root_path, 'data', project, 'Veriler.xlsx')
    df = pd.read_excel(veriler_path, sheet_name='Sayfa2', header=0)
    excel_trams = sorted([str(t) for t in df['tram_id'].dropna().unique().tolist()])
    
    print(f"📊 EXCEL: {len(excel_trams)} araç")
    print(f"   Araçlar: {excel_trams}")
    print(f"   1556 var mı? {'✅ EVET' if '1556' in excel_trams else '❌ HAYIR'}\n")
    
    # 2. Dashboard (Equipment'ten çekiliyor)
    equipment_list = Equipment.query.filter_by(
        project_code=project,
        parent_id=None
    ).order_by(Equipment.equipment_code).all()
    
    equipment_trams = sorted([eq.equipment_code for eq in equipment_list])
    print(f"📊 DASHBOARD (Equipment table): {len(equipment_trams)} araç")
    print(f"   Araçlar: {equipment_trams}")
    print(f"   1556 var mı? {'✅ EVET' if '1556' in equipment_trams else '❌ HAYIR'}\n")
    
    # 3. Servis Durumu (ServiceStatus'ten çekiliyor)
    status_records = ServiceStatus.query.filter_by(
        date=today,
        project_code=project
    ).order_by(ServiceStatus.tram_id).all()
    
    status_trams = sorted(list(set([ss.tram_id for ss in status_records])))
    print(f"📊 SERVIS DURUMU (ServiceStatus table): {len(status_trams)} araç")
    print(f"   Araçlar: {status_trams}")
    print(f"   1556 var mı? {'✅ EVET' if '1556' in status_trams else '❌ HAYIR'}\n")
    
    # 4. Bakım Planları (load_trams_from_file kullanıyor)
    from routes.maintenance import load_trams_from_file
    maintenance_trams = sorted(load_trams_from_file(project))
    print(f"📊 BAKIM PLANLARI (load_trams_from_file): {len(maintenance_trams)} araç")
    print(f"   Araçlar: {maintenance_trams}")
    print(f"   1556 var mı? {'✅ EVET' if '1556' in maintenance_trams else '❌ HAYIR'}\n")
    
    # 5. Raporlar (Excel'den çekiliyor)
    print(f"📊 RAPORLAR (Dashboard/Bakım): {len(maintenance_trams)} araç (load_trams_from_file)")
    print(f"   1556 var mı? {'✅ EVET' if '1556' in maintenance_trams else '❌ HAYIR'}\n")
    
    # Özet
    print("="*100)
    print("📋 ÖZETtOPLAM BAŞARILI KONTROLÜ")
    print("="*100)
    
    checks = {
        'Dashboard': '1556' in equipment_trams,
        'Servis Durumu': '1556' in status_trams,
        'Bakım Planları': '1556' in maintenance_trams,
        'Raporlar': '1556' in maintenance_trams,
    }
    
    all_pass = all(checks.values())
    
    for name, result in checks.items():
        status = '✅' if result else '❌'
        print(f"{status} {name}: {'GÖRÜNÜYOR' if result else 'GÖRÜNMÜYOR'}")
    
    print("\n" + "="*100)
    if all_pass:
        print("✅✅✅ TÜM ROUTE'LAR 1556'YI GÖSTERIYOR - SORUN ÇÖZÜLDÜ!")
    else:
        print("❌ HENÜZ SORUN VAR")
    print("="*100 + "\n")
