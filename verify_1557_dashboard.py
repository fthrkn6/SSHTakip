#!/usr/bin/env python3
"""Verify 1557 is available in dashboard"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment, ServiceStatus
from datetime import date

app = create_app()

with app.app_context():
    project = 'belgrad'
    
    print("\n" + "="*100)
    print("DOĞRULAMA: Dashboard'da 1557 görülüyor mu?")
    print("="*100 + "\n")
    
    # 1. Equipment'ta 1557 var mı?
    print("1. Equipment tablosu:")
    eq = Equipment.query.filter_by(
        equipment_code='1557',
        project_code=project,
        parent_id=None
    ).first()
    
    if eq:
        print(f"   ✓ 1557 var ({eq.name})")
    else:
        print(f"   ✗ 1557 YOK")
    
    # 2. ServiceStatus'ta bugünün kaydı var mı?
    print("\n2. ServiceStatus tablosu:")
    today_str = date.today().strftime('%Y-%m-%d')
    ss = ServiceStatus.query.filter_by(
        tram_id='1557',
        project_code=project,
        date=today_str
    ).first()
    
    if ss:
        print(f"   ✓ {today_str}'de kayıt var (Status: {ss.status})")
    else:
        print(f"   ✗ {today_str}'de kayıt YOK")
    
    # 3. Dashboard logic'te 1557 çıkacak mı?
    print("\n3. Dashboard Filtreleme (get_tram_ids_from_veriler logic):")
    
    # Excel'den tram_ids al (simüle)
    import pandas as pd
    import os
    veriler_path = os.path.join(app.root_path, 'data', project, 'Veriler.xlsx')
    df = pd.read_excel(veriler_path, sheet_name='Sayfa2', header=0)
    
    excel_trams = [str(t) for t in df['tram_id'].dropna().unique().tolist()]
    excel_sorted = sorted(excel_trams)
    
    print(f"   Excel tram_ids: {len(excel_sorted)} araç")
    print(f"   [{excel_sorted[0]} ... {excel_sorted[-1]}]")
    
    # Equipment filter yap
    equipment_list = Equipment.query.filter(
        Equipment.equipment_code.in_(excel_sorted),
        Equipment.parent_id.is_(None),
        Equipment.project_code == project
    ).order_by(Equipment.equipment_code).all()
    
    print(f"\n   Equipment.filter(in_tram_ids): {len(equipment_list)} aramç")
    db_sorted = [eq.equipment_code for eq in equipment_list]
    print(f"   [{db_sorted[0]} ... {db_sorted[-1]}]")
    
    # 1557 sonuçlarda var mı?
    if '1557' in db_sorted:
        print(f"\n   ✓ 1557 DASHBOARD'DA GÖRÜNECEK")
    else:
        print(f"\n   ✗ 1557 DASHBOARD'DA GÖRÜNMEYECEK")
    
    # 4. Son araç nedir?
    print(f"\n4. Dashboard'da En Son Araç:")
    if equipment_list:
        last_equipment = equipment_list[-1]
        print(f"   {last_equipment.equipment_code} ({last_equipment.name})")
        
        if last_equipment.equipment_code == '1557':
            print(f"   ✓ 1557 ÖN PLANDA (En son)")
        else:
            print(f"   ! {last_equipment.equipment_code} gösterilecek")
    
    print("\n" + "="*100)
    print(f"✓ DOĞRULAMA TAMAMLANDI - Sayfayı Yenileyin")
    print("="*100 + "\n")
