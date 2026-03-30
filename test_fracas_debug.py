#!/usr/bin/env python
"""Debug script to check FRACAS data loading"""

import pandas as pd
import os
import sys

# Get the current project or default to 'belgrad'
current_project = 'belgrad'

# Check project paths
fracas_paths = []
for project in ['belgrad', 'gebze', 'istanbul', 'kayseri', 'kocaeli', 'timisoara', 'iasi', 'samsun']:
    path = f"logs/{project}/ariza_listesi/Fracas_{project.upper()}.xlsx"
    path2 = f"logs/{project}/ariza_listesi/Fracas_*.xlsx"
    if os.path.exists(path):
        fracas_paths.append((project, path))
    else:
        # Try to find any xlsx file
        dir_path = f"logs/{project}/ariza_listesi/"
        if os.path.exists(dir_path):
            xlsx_files = [f for f in os.listdir(dir_path) if f.endswith('.xlsx') and not f.startswith('~$')]
            if xlsx_files:
                fracas_paths.append((project, os.path.join(dir_path, xlsx_files[0])))

print("=" * 80)
print("FRACAS FILES FOUND:")
print("=" * 80)

for project, path in fracas_paths:
    print(f"\n📁 Project: {project}")
    print(f"   Path: {path}")
    
    if os.path.exists(path):
        try:
            # Try to read the file
            df = pd.read_excel(path, sheet_name='FRACAS', header=3)
            df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
            
            print(f"   ✓ Loaded successfully")
            print(f"   Rows: {len(df)}")
            print(f"   Columns ({len(df.columns)}):")
            for col in df.columns[:20]:  # Show first 20 columns
                print(f"      - {col}")
            if len(df.columns) > 20:
                print(f"      ... and {len(df.columns) - 20} more columns")
            
            # Check for specific columns needed for charts
            print(f"\n   Column Search Results:")
            search_terms = {
                'araç modül': ['araç modül', 'araç modülü', 'vehicle module'],
                'tedarikçi': ['tedarikçi', 'supplier'],
                'arıza konumu': ['alt sistem', 'arıza konumu', 'failure location'],
                'arıza sınıfı': ['arıza sınıfı', 'failure class', 'sınıf'],
                'tarih': ['tarih', 'date', 'hata tarih', 'arıza tarihi']
            }
            
            for key, search_list in search_terms.items():
                found = False
                for col in df.columns:
                    col_lower = col.lower()
                    for search_term in search_list:
                        if search_term.lower() in col_lower or col_lower in search_term.lower():
                            print(f"      ✓ {key}: '{col}'")
                            found = True
                            break
                    if found:
                        break
                if not found:
                    print(f"      ✗ {key}: NOT FOUND")
        
        except Exception as e:
            print(f"   ✗ Error reading file: {e}")
    else:
        print(f"   ✗ File not found")

print("\n" + "=" * 80)
