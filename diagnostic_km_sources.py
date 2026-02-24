#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check what data each page shows"""
from app import app
from models import Equipment, db
import os, json, pandas as pd

print("\n" + "="*70)
print("[DIAGNOSTIC] KM VERISI KAYNAKLARI VE SAYFALAR")
print("="*70)

with app.app_context():
    project_code = 'belgrad'
    
    # 1. DATABASE veri
    print("\n[1] DATABASE (Equipment):")
    eqs = Equipment.query.filter_by(project_code=project_code).all()
    print(f"    Toplam: {len(eqs)} araç")
    for eq in eqs[:3]:
        print(f"    - {eq.equipment_code}: KM={eq.current_km}")
    
    # 2. EXCEL veri
    print("\n[2] EXCEL (data/belgrad/km_data.xlsx):")
    xl_file = os.path.join('data', project_code, 'km_data.xlsx')
    if os.path.exists(xl_file):
        df = pd.read_excel(xl_file)
        print(f"    Toplam: {len(df)} satır")
        print(f"    Kolonlar: {list(df.columns)}")
        print(df.head(3).to_string())
    else:
        print(f"    FILE NOT FOUND: {xl_file}")
    
    # 3. JSON veri
    print("\n[3] JSON (data/belgrad/km_data.json):")
    json_file = os.path.join('data', project_code, 'km_data.json')
    if os.path.exists(json_file):
        with open(json_file) as f:
            km_data = json.load(f)
        print(f"    Toplam: {len(km_data)} öğe")
        for k in list(km_data.keys())[:3]:
            print(f"    - {k}: {km_data[k]}")
    else:
        print(f"    FILE NOT FOUND: {json_file}")
    
    # 4. TRAMVAY-KM sayfasinin veri kaynagi
    print("\n[4] /tramvay-km SAYFASI ne gösterir?")
    print("    Kaynak: get_tramvay_list_with_km() → Equipment DB")
    
    from utils_project_excel_store import get_tramvay_list_with_km
    tramvay_list = get_tramvay_list_with_km(project_code)
    print(f"    Helper döndü: {len(tramvay_list)} tramvay")
    for tram in tramvay_list[:3]:
        print(f"    - {tram.equipment_code}: KM={tram.current_km}")
    
    # 5. BAKIM-PLANLARI sayfasinin veri kaynagi
    print("\n[5] /bakim-planlari SAYFASI ne gösterir?")
    print("    Kaynak: /bakim-planlari route'u")
    print("    (maintenance.json'dan) - kontrol edilecek")
    
    maint_file = os.path.join('data', project_code, 'maintenance.json')
    if os.path.exists(maint_file):
        with open(maint_file) as f:
            maint_data = json.load(f)
        print(f"    maintenance.json: {len(maint_data)} sistem")
        for k in list(maint_data.keys())[:2]:
            sistems = maint_data[k]
            if isinstance(sistems, dict):
                print(f"    - {k}: {len(sistems)} sistem")
    
    # 6. Senkronizasyon kontrol
    print("\n[6] SENKRONIZASYON DURUMU:")
    print("    Excel → DB: bootstrap_km_excel_from_equipment()")
    print("    DB → Excel: sync_km_excel_to_equipment()")
    
    # Excel ve DB karsilastir
    print("\n[7] EXCEL vs DB KARSILASTIRMASI:")
    if os.path.exists(xl_file):
        xl_df = pd.read_excel(xl_file)
        for idx, row in xl_df.head(3).iterrows():
            tram_id = str(row['tram_id'])
            xl_km = row['current_km']
            
            db_eq = Equipment.query.filter_by(equipment_code=tram_id, project_code=project_code).first()
            db_km = db_eq.current_km if db_eq else 'NOT FOUND'
            
            match = "✓" if xl_km == db_km else "✗"
            print(f"    {match} Tram {tram_id}: Excel={xl_km}, DB={db_km}")
    
    print("\n" + "="*70)
