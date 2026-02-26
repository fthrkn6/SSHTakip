#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KM veri dosyasını temizle - sadece doğru araçlar olsun (1531-1555)
"""
import pandas as pd
import os

km_file = os.path.join('data', 'belgrad', 'km_data.xlsx')

if os.path.exists(km_file):
    try:
        # KM dosyasını oku
        df = pd.read_excel(km_file)
        print(f"Orijinal KM araçları ({len(df)}): {sorted([str(t) for t in df['tram_id'].unique()])}")
        
        # Sadece 1531-1555 aralığında olanları tut
        valid_trams = [str(i) for i in range(1531, 1556)]
        df_clean = df[df['tram_id'].astype(str).isin(valid_trams)]
        
        print(f"Temizlenmiş KM araçları ({len(df_clean)}): {sorted([str(t) for t in df_clean['tram_id'].unique()])}")
        
        # Dosyaya kaydet
        df_clean.to_excel(km_file, index=False)
        print(f"\n✓ km_data.xlsx güncellendi - {len(df_clean)} araç kaldı")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"km_data.xlsx bulunamadı: {km_file}")
