#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check ariza sinifi structure in Veriler.xlsx"""

import pandas as pd
import os

# Veriler.xlsx'i oku
veriler_file = os.path.join('data', 'belgrad', 'Veriler.xlsx')

print("\n" + "="*80)
print("VERILER.XLSX - SAYFA2 İÇERİĞİ")
print("="*80)

if os.path.exists(veriler_file):
    try:
        # Sayfa2'yi oku başlık olmadan
        df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=None)
        
        print("\n📋 İlk 30 satır (Tamamı):")
        print("-"*80)
        for idx in range(min(30, len(df))):
            row = df.iloc[idx].tolist()
            print(f"Satır {idx:2d}: {row}")
        
        # Arıza Sınıfları bölümünü tespit et
        print("\n\n🔍 ARIZA SINIFI BÖLÜMÜNÜ ARAYORUM...")
        print("-"*80)
        
        for idx, row in df.iterrows():
            first_val = str(row[0]).strip() if pd.notna(row[0]) else ""
            if "Arıza Sınıfı" in first_val or "Ariza Sinifi" in first_val:
                print(f"✅ Bulundu! Satır {idx}: {row.tolist()}")
                
                # Sonraki satırları göster
                for next_idx in range(idx+1, min(idx+10, len(df))):
                    next_row = df.iloc[next_idx].tolist()
                    if pd.isna(next_row[0]) or str(next_row[0]).strip() == "":
                        break
                    print(f"   Satır {next_idx}: {next_row}")
    
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"❌ Dosya bulunamadı: {veriler_file}")

print("\n" + "="*80 + "\n")
