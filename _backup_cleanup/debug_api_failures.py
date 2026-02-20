#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug API failures endpoint"""

import pandas as pd
import os

ariza_listesi_dir = os.path.join(os.path.dirname(__file__), 'logs', 'ariza_listesi')
ariza_listesi_file = os.path.join(ariza_listesi_dir, 'Ariza_Listesi_BELGRAD.xlsx')

print("\n" + "="*70)
print("API FAILURES ENDPOINT DEBUG")
print("="*70)

if os.path.exists(ariza_listesi_file):
    print(f"\nFile: {ariza_listesi_file}")
    
    try:
        df = pd.read_excel(ariza_listesi_file, sheet_name='Ariza Listesi', header=3)
        
        print(f"\nTum Sutunlar ({len(df.columns)}):")
        for i, col in enumerate(df.columns):
            print(f"  {i}: '{col}'")
        
        # Arac No sutununu ara
        print(f"\n'Arac No' suesi araniyor...")
        arac_no_col = None
        for col in df.columns:
            col_lower = str(col).lower()
            if 'arac' in col_lower and 'no' in col_lower:
                arac_no_col = col
                print(f"  [BULUNDU] '{col}'")
                break
        
        if not arac_no_col:
            print(f"  [BULUNAMADI] Exact match yok")
            print(f"\n  'arac' iceren sutunlar:")
            for col in df.columns:
                if 'arac' in str(col).lower():
                    print(f"    - '{col}'")
        
        # Data check
        print(f"\nVeriler:")
        print(f"  Toplam satir: {len(df)}")
        print(f"  Ilk satir: {df.iloc[0].to_dict() if len(df) > 0 else 'YOK'}")
        
        if arac_no_col:
            print(f"\n  '{arac_no_col}' degerleri:")
            for i, val in enumerate(df[arac_no_col].head(3)):
                print(f"    {i}: {val} (type: {type(val).__name__})")
            
            # Arac 1532 araniyor
            print(f"\n  Arac 1532 araniyor...")
            filtered = df[df[arac_no_col].astype(str).str.strip() == '1532']
            print(f"    Bulunan: {len(filtered)} satir")
            if len(filtered) > 0:
                print(f"    Tek satir:")
                print(filtered.iloc[0].to_dict())
    
    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"Dosya bulunamadi: {ariza_listesi_file}")

print("\n" + "="*70 + "\n")
