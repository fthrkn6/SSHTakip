#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Final attempt - use os.replace with force"""

import pandas as pd
import os
import shutil
import tempfile
import time

excel_file = r'c:\Users\ferki\Desktop\bozankaya_ssh_takip\logs\ariza_listesi\Ariza_Listesi_BELGRAD.xlsx'
backup = excel_file.replace('.xlsx', '_backup_' + str(int(time.time())) + '.xlsx')
temp_excel = r'C:\Users\ferki\AppData\Local\Temp\Ariza_Listesi_BELGRAD_final.xlsx'

try:
    print("Step 1: Creating backup...")
    shutil.copy2(excel_file, backup)
    print(f"✅ Backup created: {backup}")
    
    print("\nStep 2: Creating updated Excel...")
    df = pd.read_excel(excel_file, sheet_name='Ariza Listesi', header=3)
    df['Personel Sayısı'] = ''
    
    with pd.ExcelWriter(temp_excel, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Ariza Listesi', startrow=3, index=False)
    
    print(f"✅ Updated file created: {temp_excel}")
    
    print("\nStep 3: Replacing original...")
    time.sleep(1)
    
    # Try different replacement methods
    try:
        # Method 1: Direct replace
        os.replace(temp_excel, excel_file)
        print("✅ File replaced successfully (method 1)")
    except:
        # Method 2: Remove and copy
        try:
            os.remove(excel_file)
            shutil.copy2(temp_excel, excel_file)
            print("✅ File replaced successfully (method 2)")
        except:
            # Method 3: Rename and copy
            os.rename(excel_file, backup.replace('_backup', '_temp_backup'))
            shutil.copy2(temp_excel, excel_file)
            os.remove(backup.replace('_backup', '_temp_backup'))
            print("✅ File replaced successfully (method 3)")
    
    # Clean up
    try:
        os.remove(temp_excel)
    except:
        pass
    
    print("\n" + "="*50)
    print("✅ SUCCESS - Personel Sayısı column added!")
    print("="*50)
    
    # Verify
    df_check = pd.read_excel(excel_file, sheet_name='Ariza Listesi', header=3)
    print(f"\nFile verification:")
    print(f"Total columns: {len(df_check.columns)}")
    print(f"Last column: {df_check.columns[-1]}")
    print(f"Location: {excel_file}")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
