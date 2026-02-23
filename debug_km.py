#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug KM sayfası - Equipment ve Excel verilerini kontrol et"""

from app import create_app, db
from models import Equipment
import pandas as pd
import os

app = create_app()

with app.app_context():
    print("="*60)
    print("PROJECT FILTERING DEBUG")
    print("="*60)
    
    # Database'deki Equipment'ları kontrol et
    print("\n1. DATABASE EQUIPMENT RECORDS:")
    print("-" * 60)
    
    belgrad_eq = Equipment.query.filter_by(project_code='belgrad').all()
    print(f"Belgrad Equipment Count: {len(belgrad_eq)}")
    if belgrad_eq:
        for eq in belgrad_eq[:3]:
            print(f"  - Code: {eq.equipment_code}, Type: {eq.equipment_type}, Project: {eq.project_code}")
    
    kayseri_eq = Equipment.query.filter_by(project_code='kayseri').all()
    print(f"\nKayseri Equipment Count: {len(kayseri_eq)}")
    if kayseri_eq:
        for eq in kayseri_eq[:3]:
            print(f"  - Code: {eq.equipment_code}, Type: {eq.equipment_type}, Project: {eq.project_code}")
    
    empty_project = Equipment.query.filter((Equipment.project_code.is_(None)) | (Equipment.project_code == '')).all()
    print(f"\nEmpty Project_Code Count: {len(empty_project)}")
    
    # Excel verilerini kontrol et
    print("\n2. EXCEL VERİLERİ (YENİ LOGIC):")
    print("-" * 60)
    
    for project in ['belgrad', 'kayseri']:
        excel_path = os.path.join('data', project, 'Veriler.xlsx')
        if os.path.exists(excel_path):
            print(f"\n{project.upper()}:")
            try:
                import pandas as pd
                xls = pd.ExcelFile(excel_path)
                print(f"  Sheet names: {xls.sheet_names}")
                
                # Hangi sheet'i okuyacağı belirle (yeni logic)
                sheet_name = None
                if 'Sayfa2' in xls.sheet_names:
                    sheet_name = 'Sayfa2'
                elif len(xls.sheet_names) > 0:
                    sheet_name = xls.sheet_names[0]
                
                print(f"  Using sheet: {sheet_name}")
                
                if sheet_name:
                    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=0, engine='openpyxl')
                    print(f"  Columns: {list(df.columns)}")
                    print(f"  Shape: {df.shape}")
                    
                    # First col'u al
                    first_col = df.columns[0]
                    print(f"  First column: {first_col}")
                    
                    tram_ids = []
                    for idx, row in df.iterrows():
                        tram_id = str(row[first_col]).strip() if pd.notna(row[first_col]) else None
                        if tram_id and tram_id.lower() not in ['project', 'proje', 'nan', '']:
                            tram_ids.append(tram_id)
                    
                    print(f"  Extracted tram_ids: {tram_ids[:5]}")
                    
            except Exception as e:
                print(f"  Error: {e}")
        else:
            print(f"\n{project.upper()}: Excel file not found")

print("\n" + "="*60)
print("DEBUG COMPLETE")
print("="*60)
