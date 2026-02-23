#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test: Excel tram_id vs Database equipment_code matching"""

from app import create_app, db
from models import Equipment
import pandas as pd
import os

app = create_app()

with app.app_context():
    print("\n" + "="*70)
    print("EXCEL vs DATABASE MATCHING TEST")
    print("="*70)
    
    for project in ['belgrad', 'kayseri']:
        print(f"\n{project.upper()}:")
        print("-" * 70)
        
        # Excel tram_id'leri oku
        excel_path = os.path.join('data', project, 'Veriler.xlsx')
        xls = pd.ExcelFile(excel_path)
        sheet_name = 'Sayfa2' if 'Sayfa2' in xls.sheet_names else xls.sheet_names[0]
        df = pd.read_excel(excel_path, sheet_name=sheet_name, header=0, engine='openpyxl')
        
        excel_ids = []
        tram_col = df.columns[0]
        for idx, row in df.iterrows():
            val = str(row[tram_col]).strip() if pd.notna(row[tram_col]) else None
            if val and val.lower() not in ['project', 'proje', 'nan', '']:
                excel_ids.append(val)
        
        print(f"Excel {sheet_name} tram_ids: {excel_ids[:5]}... (total: {len(excel_ids)})")
        
        # Database Equipment'ları oku
        db_equips = Equipment.query.filter_by(project_code=project).all()
        db_codes = [e.equipment_code for e in db_equips]
        print(f"Database equipment_codes: {[c for c in db_codes[:5]]}... (total: {len(db_codes)})")
        
        # Test: Her Excel ID için database'de bul
        print(f"\nMatching test:")
        matched = 0
        not_matched = []
        for excel_id in excel_ids[:10]:  # İlk 10'unu test et
            equipment = Equipment.query.filter_by(equipment_code=str(excel_id), project_code=project).first()
            if equipment:
                matched += 1
                print(f"  [OK] {excel_id} -> Found in DB")
            else:
                not_matched.append(excel_id)
                # Debug: Database'de hangi equipment varsa göster
                all_with_similar = Equipment.query.filter(Equipment.equipment_code.like(f"%{excel_id}%")).all()
                if all_with_similar:
                    print(f"  [NO] {excel_id} -> NOT found, similar: {[e.equipment_code for e in all_with_similar]}")
                else:
                    print(f"  [NO] {excel_id} -> NOT found at all")
        
        print(f"\nMatched: {matched}/10, Not matched: {len(not_matched)}")
        if not_matched:
            print(f"  Problem IDs: {not_matched}")

print("\n" + "="*70)
