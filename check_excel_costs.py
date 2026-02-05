#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import os

excel_path = 'data/belgrad/BEL25_FRACAS.xlsx'
df = pd.read_excel(excel_path, sheet_name='FRACAS', header=0)

print("Malzeme/İşçilik/Bekleme Süresi Sütunları:")
print("=" * 80)

for i, col in enumerate(df.columns):
    col_lower = col.lower()
    if any(x in col_lower for x in ['maliyet', 'cost', 'bekleme', 'waiting']):
        print(f"\n{i+1}. {col}")
        print(f"   Veri: {df[col].head(3).tolist()}")
        print(f"   Boş satırlar: {df[col].isna().sum()}")
        print(f"   Unique: {df[col].nunique()}")

print("\n\nTüm sütunlar:")
for i, col in enumerate(df.columns):
    print(f"{i+1:2d}. {col}")
