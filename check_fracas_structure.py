#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FRACAS Excel dosyasini analiz et - sutun adlarini ve icerigi goster
"""

import pandas as pd
import os

project = 'BELGRAD'
ariza_listesi_dir = os.path.join('logs', project, 'ariza_listesi')

print("FRACAS Excel Analizi")
print("=" * 100)

if os.path.exists(ariza_listesi_dir):
    for file in os.listdir(ariza_listesi_dir):
        if file.upper().startswith('FRACAS_') and file.endswith('.xlsx') and not file.startswith('~$'):
            filepath = os.path.join(ariza_listesi_dir, file)
            print(f"Dosya: {file}\n")
            
            df = pd.read_excel(filepath, sheet_name='FRACAS', header=3)
            
            print(f"SUTUN ADLARI (Toplam: {len(df.columns)})")
            print("-" * 100)
            for idx, col in enumerate(df.columns):
                print(f"[{idx:2d}] {col}")
            
            print(f"\n\nILK 3 SATIR ORNEK:")
            print("-" * 100)
            print(df.head(3).to_string())
            
            break
