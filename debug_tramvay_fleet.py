#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tramvay Filosu Debug Script
Dashboard'da neden görünmediğini kontrol et
"""

import os
import sys
import pandas as pd

# App context
sys.path.insert(0, os.path.dirname(__file__))

# Create app
from app import create_app
from models import db, Equipment

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("TRAMVAY FİLOSU DEBUG")
    print("="*80)
    
    # Test her proje için
    for project in ['belgrad', 'kayseri']:
        print(f"\n📍 PROJECT: {project.upper()}")
        print("-" * 80)
        
        # 1. Veriler.xlsx'tan tram_id'leri çek
        veriler_path = os.path.join(app.root_path, 'data', project, 'Veriler.xlsx')
        print(f"\n1️⃣  Veriler.xlsx: {veriler_path}")
        print(f"   Var mı? {os.path.exists(veriler_path)}")
        
        tram_ids_from_excel = []
        if os.path.exists(veriler_path):
            try:
                df = pd.read_excel(veriler_path, sheet_name='Sayfa2', header=0)
                print(f"   Columns: {list(df.columns)}")
                
                if 'tram_id' in df.columns:
                    tram_ids_from_excel = df['tram_id'].dropna().unique().tolist()
                    print(f"   ✅ tram_id bulundu! Count: {len(tram_ids_from_excel)}")
                    print(f"   Values: {tram_ids_from_excel[:10]}")
                else:
                    print(f"   ❌ 'tram_id' sütunu bulunamadı!")
                    print(f"   Available columns: {list(df.columns)}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # 2. Equipment tablosunda ne var?
        print(f"\n2️⃣  Equipment Tablosu (parent_id=None):")
        equipment_list = Equipment.query.filter_by(parent_id=None).all()
        print(f"   Total count: {len(equipment_list)}")
        
        if equipment_list:
            print(f"   Equipment codes:")
            for eq in equipment_list[:10]:
                print(f"     - ID: {eq.id}, Code: {eq.equipment_code}, Name: {eq.name}")
            if len(equipment_list) > 10:
                print(f"     ... and {len(equipment_list) - 10} more")
        else:
            print(f"   ⚠️  Boş!")
        
        # 3. Eşleştirme kontrol et
        print(f"\n3️⃣  Eşleştirme Kontrolü:")
        if tram_ids_from_excel and equipment_list:
            equipment_codes = {eq.equipment_code for eq in equipment_list}
            excel_tram_ids = {str(t) for t in tram_ids_from_excel}
            
            print(f"   Excel tram_id'ler: {excel_tram_ids}")
            print(f"   Equipment codes: {equipment_codes}")
            
            match = excel_tram_ids.intersection(equipment_codes)
            print(f"   ✅ Eşleşen: {match}")
            
            not_in_db = excel_tram_ids - equipment_codes
            if not_in_db:
                print(f"   ⚠️  Excel'de var ama DB'de yok: {not_in_db}")
            
            not_in_excel = equipment_codes - excel_tram_ids
            if not_in_excel:
                print(f"   ℹ️  DB'de var ama Excel'de yok: {not_in_excel}")
        elif tram_ids_from_excel and not equipment_list:
            print(f"   ❌ Excel'de tram_id var ama Equipment tablosu boş!")
        elif not tram_ids_from_excel and equipment_list:
            print(f"   ⚠️  Excel'de tram_id yok ama Equipment'ta var (fallback çalışacak)")
        else:
            print(f"   ❌ Her iki yerde de veri yok!")
    
    print("\n" + "="*80)
