#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

excel_path = r'c:\Users\ferki\Desktop\bozankaya_ssh_takip\data\belgrad\BEL25_FRACAS.xlsx'
df = pd.read_excel(excel_path, sheet_name='FRACAS', header=0, engine='openpyxl')

print('='*80)
print('EXCEL DETAYLI ANALIZ')
print('='*80)

# FRACAS ID sütununu bul
fracas_col = None
for col in df.columns:
    if 'fracas' in col.lower() and 'id' in col.lower():
        fracas_col = col
        break

print(f'\nFRACAS ID Sütunu: {fracas_col}')
print(f'Toplam satır: {len(df)}')

# Her satırın doluluk analizi
print('\nSatır Analizi (İlk 15 satır):')
for idx in range(min(15, len(df))):
    row = df.iloc[idx]
    fracas_id = row.get(fracas_col, np.nan)
    non_null = row.notna().sum()
    
    if pd.isna(fracas_id):
        fracas_id = "NaN"
    else:
        fracas_id = str(fracas_id)
    
    # Bu satırda veri olan sütunları say
    filled_cols = [col for col in df.columns if pd.notna(row.get(col))]
    
    print(f'Satır {idx+1:2d}: FRACAS ID={fracas_id:20s} | Dolu: {non_null:2d}/{len(df.columns)} sütun')
    
    if filled_cols and len(filled_cols) > 0:
        # İlk 3 dolu sütunu göster
        samples = [f"{col[:20]}={str(row.get(col))[:15]}" for col in filled_cols[:3]]
        print(f'          Veriler: {" | ".join(samples)}')
