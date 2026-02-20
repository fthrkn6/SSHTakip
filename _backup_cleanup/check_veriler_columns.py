#!/usr/bin/env python3
"""Check column names in Veriler.xlsx for each project"""
import os
import pandas as pd

projects = ['belgrad', 'kayseri', 'iasi', 'timisoara', 'kocaeli', 'gebze']
root_path = '.'

for project in projects:
    excel_path = os.path.join(root_path, 'data', project, 'Veriler.xlsx')
    print(f"\n{project.upper()}:")
    print(f"  File: {excel_path}")
    
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path, sheet_name='Sayfa2', header=0)
            print(f"  Columns: {list(df.columns)}")
            print(f"  Rows: {len(df)}")
            # Print first few rows
            if 'tram_id' in df.columns:
                print(f"  Sample tram_ids: {df['tram_id'].head(3).tolist()}")
            elif 'equipment_code' in df.columns:
                print(f"  Sample equipment_codes: {df['equipment_code'].head(3).tolist()}")
            else:
                print(f"  First column values: {df.iloc[:, 0].head(3).tolist()}")
        except Exception as e:
            print(f"  Error: {str(e)}")
    else:
        print(f"  ❌ File not found")
