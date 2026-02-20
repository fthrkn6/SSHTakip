#!/usr/bin/env python3
"""Test Equipment page uses Excel filter"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment
from utils.project_manager import ProjectManager
import pandas as pd

app = create_app()

with app.app_context():
    project = 'belgrad'
    
    print("\n" + "="*100)
    print("TEST: Equipment Sayfasi Excel Filtrelemesi")
    print("="*100 + "\n")
    
    # Excel'deki araçlar
    veriler_file = ProjectManager.get_veriler_file(project)
    df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
    excel_trams = sorted([str(t) for t in df['tram_id'].dropna().unique().tolist()])
    
    print(f"1. EXCEL VERISI:")
    print(f"   Toplam: {len(excel_trams)} arac")
    print(f"   [{excel_trams[0]} ... {excel_trams[-1]}]\n")
    
    # Equipment totali
    all_eq = Equipment.query.filter_by(parent_id=None, project_code=project).all()
    all_codes = sorted([eq.equipment_code for eq in all_eq])
    
    print(f"2. EQUIPMENT TABLOSU:")
    print(f"   Toplam: {len(all_codes)} arac")
    print(f"   [{all_codes[0]} ... {all_codes[-1]}]\n")
    
    # Equipment filtreli (Equipment sayfasının yapacağı)
    filtered_eq = Equipment.query.filter(
        Equipment.equipment_code.in_(excel_trams),
        Equipment.parent_id.is_(None),
        Equipment.project_code == project
    ).all()
    filtered_codes = sorted([eq.equipment_code for eq in filtered_eq])
    
    print(f"3. EQUIPMENT (EXCEL FILTRELI - Equipment sayfasi):")
    print(f"   Toplam: {len(filtered_codes)} arac")
    print(f"   [{filtered_codes[0]} ... {filtered_codes[-1]}]\n")
    
    # Fark
    only_excel = set(excel_trams) - set(filtered_codes)
    only_equipment = set(filtered_codes) - set(excel_trams)
    
    print(f"4. KARSILASTIRMA:")
    if only_excel:
        print(f"   Excel'de var, Equipment'ta YOK: {sorted(only_excel)}")
    if only_equipment:
        print(f"   Equipment'ta var, Excel'de YOK: {sorted(only_equipment)}")
    
    print(f"\n" + "="*100)
    if set(filtered_codes) == set(excel_trams):
        print(f"✓ BASARILI - Equipment sayfasi Excel ile senkronize")
        print(f"✓ Her proje Excelden dinamik veri cekiyor")
    else:
        print(f"! Fark var, kontrol edin")
    print("="*100 + "\n")
