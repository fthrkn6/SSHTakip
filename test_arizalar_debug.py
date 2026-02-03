#!/usr/bin/env python
"""Test /arizalar route without HTTP"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.getcwd())

from routes.fracas import get_excel_path

# Simulate getting Excel path
project_folder = os.path.join(os.getcwd(), 'data', 'belgrad')
print(f"Project folder: {project_folder}")
print(f"Files in folder:")
for f in os.listdir(project_folder):
    if f.endswith(('.xlsx', '.xls')):
        print(f"  - {f}")

# Direct path
excel_path = None
for filename in os.listdir(project_folder):
    if 'fracas' in filename.lower() and filename.endswith(('.xlsx', '.xls')) and not filename.startswith('~$'):
        excel_path = os.path.join(project_folder, filename)
        break

print(f"\nFound Excel path: {excel_path}")
print(f"File exists: {os.path.exists(excel_path) if excel_path else 'No path'}")

if excel_path and os.path.exists(excel_path):
    try:
        print(f"\nReading Excel file...")
        df = pd.read_excel(excel_path, sheet_name='FRACAS', header=3)
        print(f"DataFrame shape: {df.shape}")
        print(f"Columns: {list(df.columns)[:5]}")
        
        df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
        
        # Find FRACAS ID column
        fracas_col = None
        for col in df.columns:
            if 'fracas' in col.lower() and 'id' in col.lower():
                fracas_col = col
                break
        
        print(f"FRACAS ID column: {fracas_col}")
        
        if fracas_col:
            non_empty = df[fracas_col].notna().sum()
            print(f"Non-empty FRACAS IDs: {non_empty}")
            
            df_clean = df[df[fracas_col].notna()].copy()
            print(f"Rows after cleanup: {len(df_clean)}")
            
            if len(df_clean) > 0:
                print(f"\nFirst 3 FRACAS records:")
                for idx, (_, row) in enumerate(df_clean.head(3).iterrows(), 1):
                    fracas_id = row.get(fracas_col, 'N/A')
                    print(f"  {idx}. {fracas_id}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
