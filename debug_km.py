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
    print("\n2. EXCEL VERİLERİ:")
    print("-" * 60)
    
    for project in ['belgrad', 'kayseri']:
        excel_path = os.path.join('data', project, 'Veriler.xlsx')
        if os.path.exists(excel_path):
            print(f"\n{project.upper()}:")
            try:
                xls = pd.ExcelFile(excel_path)
                print(f"  Sheet names: {xls.sheet_names}")
                
                df = pd.read_excel(excel_path, sheet_name=0, header=0, engine='openpyxl')
                print(f"  Shape: {df.shape}")
                print(f"  Columns: {list(df.columns)}")
                
                # tram_id sütununu bul
                tram_id_col = None
                for col in df.columns:
                    if 'tram' in col.lower() or 'id' in col.lower():
                        print(f"  Potential tram_id column: {col}")
                        if col.lower() == 'tram_id':
                            tram_id_col = col
                            break
                
                if tram_id_col:
                    unique_ids = df[tram_id_col].dropna().unique()[:5]
                    print(f"  First 5 tram_ids: {list(unique_ids)}")
                else:
                    print(f"  No 'tram_id' column found!")
                    print(f"  First row: {df.iloc[0].to_dict()}")
                    
            except Exception as e:
                print(f"  Error reading: {e}")
        else:
            print(f"\n{project.upper()}: Excel file not found at {excel_path}")

print("\n" + "="*60)
print("DEBUG COMPLETE")
print("="*60)
