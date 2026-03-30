#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import os

belgrad_file = r'logs\belgrad\ariza_listesi\Fracas_BELGRAD.xlsx'

print("BELGRAD FILE TEST")
print("=" * 60)

print(f"\n1. File exists: {os.path.exists(belgrad_file)}")

if os.path.exists(belgrad_file):
    try:
        print("\n2. Reading Excel file...")
        xls = pd.ExcelFile(belgrad_file)
        print(f"   Sheet names: {xls.sheet_names}")
        
        if 'FRACAS' in xls.sheet_names:
            print("\n3. Reading FRACAS sheet with header=3...")
            df = pd.read_excel(belgrad_file, sheet_name='FRACAS', header=3)
            print(f"   SUCCESS: {len(df)} rows loaded")
            print(f"   Columns: {list(df.columns)[:5]}...")
        else:
            print("\n   WARNING: FRACAS sheet not found!")
            
    except Exception as e:
        import traceback
        print(f"\n   ERROR: {e}")
        traceback.print_exc()

print("\n" + "=" * 60)
