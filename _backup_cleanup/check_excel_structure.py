#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check Excel file structure"""

import pandas as pd
import os

excel_file = r'c:\Users\ferki\Desktop\bozankaya_ssh_takip\logs\ariza_listesi\Ariza_Listesi_BELGRAD.xlsx'

if os.path.exists(excel_file):
    df = pd.read_excel(excel_file, sheet_name='Ariza Listesi', header=3)
    print("Column Headers:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")
    
    print(f"\nTotal columns: {len(df.columns)}")
    print(f"\nFirst row data:")
    if len(df) > 0:
        first_row = df.iloc[0]
        for i, val in enumerate(first_row):
            print(f"{i}: {val}")
else:
    print("File not found!")
