#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check ariza listesi structure and classes"""

import pandas as pd
import os

print("\n" + "="*80)
print("ARIZA_LISTESI_BELGRAD.XLSX YAPISI")
print("="*80)

ariza_file = os.path.join('logs', 'ariza_listesi', 'Ariza_Listesi_BELGRAD.xlsx')

if os.path.exists(ariza_file):
    try:
        # Sheet'leri listele
        excel_file = pd.ExcelFile(ariza_file)
        print(f"\n📄 Sheet'ler: {excel_file.sheet_names}")
        
        # 'Ariza Listesi' sheet'ini oku
        df = pd.read_excel(ariza_file, sheet_name='Ariza Listesi', header=3)
        
        print(f"\n📊 Sütunlar: {df.columns.tolist()}")
        print(f"📊 Toplam satır: {len(df)}")
        
        print(f"\n📋 Tüm arızalar:")
        print("-"*80)
        print(df.to_string())
        
        # Arıza Sınıfı sütununu kontrol et
        if 'Arıza Sınıfı' in df.columns:
            print(f"\n\n🎯 ARIZA SINIFI DAĞILIMI:")
            print("-"*80)
            sinif_counts = df['Arıza Sınıfı'].value_counts()
            for sinif, count in sinif_counts.items():
                print(f"   {sinif}: {count}")
        else:
            print("\n⚠️  'Arıza Sınıfı' sütunu bulunamadı!")
            print(f"   Mevcut sütunlar: {df.columns.tolist()}")
    
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"❌ Dosya bulunamadı: {ariza_file}")

print("\n" + "="*80 + "\n")
