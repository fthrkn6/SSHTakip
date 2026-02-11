#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Add Personnel Count column by copying to temp location"""

import pandas as pd
import os
import shutil
import tempfile

excel_file = r'c:\Users\ferki\Desktop\bozankaya_ssh_takip\logs\ariza_listesi\Ariza_Listesi_BELGRAD.xlsx'
temp_dir = tempfile.gettempdir()
temp_excel = os.path.join(temp_dir, 'Ariza_Listesi_BELGRAD_edit.xlsx')

try:
    # Step 1: Copy to temp location
    print(f"📋 Dosya kopyalanıyor: {excel_file}")
    shutil.copy2(excel_file, temp_excel)
    print(f"✅ Geçici konuma kopyalandı: {temp_dir}")
    
    # Step 2: Read and modify
    print(f"📖 Veriler okunuyor...")
    df = pd.read_excel(temp_excel, sheet_name='Ariza Listesi', header=3)
    
    # Add new column
    df['Personel Sayısı'] = ''
    print(f"✅ Yeni sütun eklendi: '{df.columns[-1]}'")
    
    # Step 3: Write modified file
    print(f"💾 Dosya yazılıyor...")
    with pd.ExcelWriter(temp_excel, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Ariza Listesi', startrow=3, index=False)
    
    # Step 4: Copy back
    print(f"📂 Orijinal konuma kopyalanıyor...")
    shutil.copy2(temp_excel, excel_file)
    
    # Step 5: Clean up
    os.remove(temp_excel)
    
    print(f"\n✅ Tamamlandı!")
    print(f"Dosya: {excel_file}")
    
    # Verify
    df_check = pd.read_excel(excel_file, sheet_name='Ariza Listesi', header=3)
    print(f"\n📊 Başarılı!")
    print(f"Toplam sütun: {len(df_check.columns)}")
    print(f"Son sütunlar: {', '.join(df_check.columns[-3:].tolist())}")
    
except Exception as e:
    print(f"❌ Hata: {str(e)}")
    import traceback
    traceback.print_exc()
    # Clean up
    if os.path.exists(temp_excel):
        try:
            os.remove(temp_excel)
        except:
            pass
