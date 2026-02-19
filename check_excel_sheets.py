#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import os

excel_file = 'logs/belgrad/ariza_listesi/Fracas_BELGRAD.xlsx'

if os.path.exists(excel_file):
    print(f"✓ Dosya bulundu: {excel_file}")
    print()
    
    try:
        xl_file = pd.ExcelFile(excel_file)
        print(f"Sheet adları: {xl_file.sheet_names}")
        print()
        
        for sheet_name in xl_file.sheet_names:
            print(f"=== Sheet: {sheet_name} ===")
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
            print(f"Satır: {len(df)}, Sütun: {len(df.columns)}")
            print("İlk 3 satır:")
            print(df.head(3))
            print()
    except Exception as e:
        print(f"❌ Hata: {e}")
else:
    print(f"❌ Dosya bulunamadı: {excel_file}")
