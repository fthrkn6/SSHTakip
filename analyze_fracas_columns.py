#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FRACAS Excel dosyasını analiz et - sütun adlarını ve içeriğini göster
"""

import pandas as pd
import os

project = 'BELGRAD'
ariza_listesi_dir = os.path.join('logs', project, 'ariza_listesi')

print("📊 FRACAS Excel Analizi")
print("=" * 100)

if os.path.exists(ariza_listesi_dir):
    for file in os.listdir(ariza_listesi_dir):
        if file.upper().startswith('FRACAS_') and file.endswith('.xlsx') and not file.startswith('~$'):
            filepath = os.path.join(ariza_listesi_dir, file)
            print(f"📄 Dosya: {file}")
            
            # Header row 3 (index 3) = row 4
            df = pd.read_excel(filepath, sheet_name='FRACAS', header=3)
            
            print(f"\n📋 Sütun Adları (Toplam: {len(df.columns)})")
            print("-" * 100)
            for idx, col in enumerate(df.columns):
                print(f"  [{idx:2d}] {col}")
            
            # Parça Kodu ara
            parca_kodu_col = None
            parca_adi_col = None
            mttr_col = None
            
            for idx, col in enumerate(df.columns):
                col_lower = str(col).lower()
                if 'parça' in col_lower and 'kodu' in col_lower:
                    parca_kodu_col = idx
                if 'parça' in col_lower and 'adı' in col_lower:
                    parca_adi_col = idx
                if 'mttr' in col_lower or 'ortalama' in col_lower and 'onarım' in col_lower:
                    mttr_col = idx
            
            print(f"\n📌 Bulunan Sütunlar:")
            print(f"  Parça Kodu: Index {parca_kodu_col} ({df.columns[parca_kodu_col] if parca_kodu_col is not None else 'Bulunamadı'})")
            print(f"  Parça Adı: Index {parca_adi_col} ({df.columns[parca_adi_col] if parca_adi_col is not None else 'Bulunamadı'})")
            print(f"  MTTR: Index {mttr_col} ({df.columns[mttr_col] if mttr_col is not None else 'Bulunamadı'})")
            
            print(f"\n📊 İlk 3 Satır Örneği:")
            print("-" * 100)
            print(df.head(3).to_string())
            
            break
