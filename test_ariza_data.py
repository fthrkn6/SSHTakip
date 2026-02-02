#!/usr/bin/env python
"""Arıza verilerini test et"""
import os
import sys
import pandas as pd

# Belgrad klasörüne git
belgrad_path = os.path.join('data', 'belgrad')
print(f"🔍 Belgrad Klasörü: {belgrad_path}")
print(f"✓ Klasör Var mı: {os.path.exists(belgrad_path)}")

if os.path.exists(belgrad_path):
    files = os.listdir(belgrad_path)
    print(f"\n📁 Dosyalar ({len(files)}):")
    for f in files:
        print(f"  - {f}")
    
    # FRACAS dosyasını bul
    fracas_file = None
    for f in files:
        if 'fracas' in f.lower() and f.endswith(('.xlsx', '.xls')):
            fracas_file = os.path.join(belgrad_path, f)
            print(f"\n✓ FRACAS Dosyası Bulundu: {f}")
            break
    
    if fracas_file:
        try:
            print(f"\n📊 Excel Okunuyor...")
            df = pd.read_excel(fracas_file, sheet_name='FRACAS', header=3)
            print(f"✓ DataFrame Shape: {df.shape}")
            print(f"✓ Sütunlar: {list(df.columns)[:10]}")
            print(f"\n✓ İlk 3 Satır:")
            print(df.head(3).to_string())
        except Exception as e:
            print(f"❌ Hata: {e}")
            import traceback
            traceback.print_exc()
else:
    print(f"❌ Klasör bulunamadı!")
