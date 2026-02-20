#!/usr/bin/env python3
"""Compare Excel vs Equipment vs Dashboard data"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment, ServiceStatus
from utils.project_manager import ProjectManager
import pandas as pd
from datetime import date

app = create_app()

with app.app_context():
    project = 'belgrad'
    today = date.today().strftime('%Y-%m-%d')
    
    print("\n" + "="*100)
    print("VERI KAYNAKLARI KARSILASTIRMASI - Tramvay Fleet")
    print("="*100 + "\n")
    
    # 1. EXCEL'DEN VERİ
    print("1. EXCEL'DEN TRAM_IDS (Veriler.xlsx - Sayfa2):")
    veriler_file = ProjectManager.get_veriler_file(project)
    df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
    excel_trams = sorted([str(t) for t in df['tram_id'].dropna().unique().tolist()])
    print(f"   Toplam: {len(excel_trams)}")
    print(f"   [{excel_trams[0]} ... {excel_trams[-1]}]")
    print(f"   Veriler: {excel_trams}\n")
    
    # 2. EQUIPMENT'TAN VERİ (NO FILTER)
    print("2. EQUIPMENT TABLOSUNDAN (Tum araçlar, filter YOK):")
    all_equipment = Equipment.query.filter_by(parent_id=None, project_code=project).order_by(Equipment.equipment_code).all()
    all_codes = sorted([eq.equipment_code for eq in all_equipment])
    print(f"   Toplam: {len(all_codes)}")
    print(f"   [{all_codes[0]} ... {all_codes[-1]}]")
    print(f"   Veriler: {all_codes}\n")
    
    # 3. EQUIPMENT'TAN VERİ (EXCEL FILTER APPLIED)
    print("3. EQUIPMENT FILTERED (Excel'e gore filter ile):")
    filtered_equip = Equipment.query.filter(
        Equipment.equipment_code.in_(excel_trams),
        Equipment.parent_id.is_(None),
        Equipment.project_code == project
    ).order_by(Equipment.equipment_code).all()
    filtered_codes = [eq.equipment_code for eq in filtered_equip]
    print(f"   Toplam: {len(filtered_codes)}")
    if filtered_codes:
        print(f"   [{filtered_codes[0]} ... {filtered_codes[-1]}]")
    print(f"   Veriler: {filtered_codes}\n")
    
    # 4. EXCEL VS EQUIPMENT KARSILASTIR
    print("4. FARK ANALIZI:")
    excel_set = set(excel_trams)
    all_set = set(all_codes)
    filtered_set = set(filtered_codes)
    
    only_in_excel = excel_set - all_set
    only_in_equip = all_set - excel_set
    should_show = excel_set & all_set  # Excel'de var VE Equipment'ta var
    
    print(f"   Excel'de var ama Equipment'ta YOK: {sorted(only_in_excel)}")
    print(f"   Equipment'ta var ama Excel'de YOK: {sorted(only_in_equip)}")
    print(f"   IKI TARAFTA DA VAR (Gösterilmeli): {len(should_show)} araç\n")
    
    # 5. DASHBOARD'TA NE GÖSTERILECEK?
    print("5. DASHBOARD'TA GÖSTERILECEK (get_tram_ids_from_veriler logic):")
    from routes.dashboard import get_tram_ids_from_veriler
    dashboard_trams = get_tram_ids_from_veriler(project)
    print(f"   get_tram_ids_from_veriler(): {len(dashboard_trams)} araç")
    print(f"   Veriler: {sorted(dashboard_trams)}\n")
    
    # 6. DASHBOARD FILTER SONUCU
    print("6. DASHBOARD FİLTRE SONUCU:")
    display = Equipment.query.filter(
        Equipment.equipment_code.in_(dashboard_trams),
        Equipment.parent_id.is_(None),
        Equipment.project_code == project
    ).order_by(Equipment.equipment_code).all()
    display_codes = [eq.equipment_code for eq in display]
    print(f"   Gösterilecek: {len(display_codes)} araç")
    print(f"   Veriler: {display_codes}\n")
    
    # 7. SORUN ANALIZI
    print("7. SORUN TESPİTİ:")
    if set(display_codes) == excel_set:
        print(f"   ✓ TAMAM - Display = Excel")
    elif set(display_codes) == all_set:
        print(f"   ✗ PROBLEM - Display = All Equipment (FILTER ÇALIŞMIYOR)")
        print(f"     -> Excel'de olmayan araçlar gösteriliyor!")
    else:
        print(f"   ? UNUSUAL - Display ≠ Excel ve ≠ All")
        only_display = set(display_codes) - excel_set
        missing_display = excel_set - set(display_codes)
        if only_display:
            print(f"     Excel'de YOK ama göster: {sorted(only_display)}")
        if missing_display:
            print(f"     Excel'de VAR ama göster degil: {sorted(missing_display)}")
    
    print("\n" + "="*100)
    print("SONUC")
    print("="*100 + "\n")
