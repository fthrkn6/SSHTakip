#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Add Personnel Count column to Excel - rename and recreate method"""

import pandas as pd
import os
import time

excel_file = r'c:\Users\ferki\Desktop\bozankaya_ssh_takip\logs\ariza_listesi\Ariza_Listesi_BELGRAD.xlsx'
temp_file = excel_file.replace('.xlsx', '_temp.xlsx')

try:
    # Read the Excel file with timeout retry
    for attempt in range(3):
        try:
            df = pd.read_excel(excel_file, sheet_name='Ariza Listesi', header=3)
            break
        except:
            if attempt < 2:
                time.sleep(1)
            else:
                raise
    
    # Add new column "Personel Sayısı" at the end
    df['Personel Sayısı'] = ''
    
    print(f"✅ Yeni sütun eklendi: 'Personel Sayısı' (Sütun {len(df.columns)})")
    
    # Write to temp file
    with pd.ExcelWriter(temp_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Ariza Listesi', startrow=3, index=False)
    
    print(f"✅ Geçici dosya oluşturuldu")
    time.sleep(1)
    
    # Replace original file
    if os.path.exists(temp_file):
        os.replace(temp_file, excel_file)
        print(f"✅ Orijinal dosya güncellendi!")
        
        # Verify
        df_check = pd.read_excel(excel_file, sheet_name='Ariza Listesi', header=3)
        print(f"\n✅ Başarı! Toplam sütun: {len(df_check.columns)}")
        print(f"Son sütun: {df_check.columns[-1]}")
    
except Exception as e:
    print(f"❌ Hata: {str(e)}")
    # Clean up temp file
    if os.path.exists(temp_file):
        try:
            os.remove(temp_file)
        except:
            pass
