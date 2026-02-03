#!/usr/bin/env python
"""Test /arizalar endpoint directly without Flask HTTP"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add current dir to path
sys.path.insert(0, os.getcwd())

# Import Flask app functions
from routes.fracas import get_excel_path

def test_arizalar_data():
    """Test if /arizalar route can load data from Excel"""
    
    print("="*80)
    print("TEST: /arizalar Endpoint Data Loading")
    print("="*80)
    
    # Get Excel path
    excel_path = get_excel_path()
    print(f"\n✓ Excel Path: {excel_path}")
    print(f"✓ File Exists: {os.path.exists(excel_path) if excel_path else 'No path'}")
    
    if not excel_path or not os.path.exists(excel_path):
        print("❌ Excel file not found!")
        return False
    
    # Load Excel data
    try:
        print(f"\n✓ Loading Excel sheet 'FRACAS'...")
        df = pd.read_excel(excel_path, sheet_name='FRACAS', header=3)
        
        print(f"✓ DataFrame Shape: {df.shape}")
        print(f"✓ Columns: {list(df.columns)[:5]}...")
        
        # Clean whitespace in column names
        df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
        
        # Find FRACAS ID column
        fracas_col = None
        for col in df.columns:
            if 'fracas' in col.lower() and 'id' in col.lower():
                fracas_col = col
                break
        
        print(f"\n✓ FRACAS ID Column: {fracas_col}")
        if fracas_col:
            non_empty = df[fracas_col].notna().sum()
            print(f"✓ Non-empty FRACAS ID rows: {non_empty}")
            
            # Filter empty rows
            df_clean = df[df[fracas_col].notna()].copy()
            print(f"✓ Rows after cleanup: {len(df_clean)}")
            
            if len(df_clean) > 0:
                print(f"\n✓ SUCCESS! {len(df_clean)} arıza records found")
                
                # Show first 3 records
                print(f"\n{'─'*80}")
                print("FIRST 3 RECORDS:")
                print(f"{'─'*80}")
                
                for idx, (_, row) in enumerate(df_clean.head(3).iterrows(), 1):
                    fracas_id = row.get(fracas_col, 'N/A')
                    print(f"\n{idx}. FRACAS ID: {fracas_id}")
                    
                    # Show key columns
                    for col in list(df_clean.columns)[:8]:
                        val = row.get(col, '-')
                        if pd.notna(val) and str(val).strip() and str(val) != 'nan':
                            print(f"   {col}: {val}")
                
                print(f"\n{'─'*80}")
                return True
            else:
                print(f"❌ No data rows found after cleanup")
                return False
        else:
            print(f"❌ FRACAS ID column not found")
            return False
            
    except Exception as e:
        print(f"❌ Error loading Excel: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_arizalar_data()
    sys.exit(0 if success else 1)
