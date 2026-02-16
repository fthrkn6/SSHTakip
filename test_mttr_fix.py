#!/usr/bin/env python3
"""Düzeltilmiş MTTR hesaplamasını test etmek için"""

import pandas as pd
import re

filepath = r'c:\Users\ferki\Desktop\bozankaya_ssh_takip\logs\belgrad\ariza_listesi\Ariza_Listesi_BELGRAD.xlsx'

df = pd.read_excel(filepath, sheet_name='Ariza Listesi', header=3)

mttr_col = 'MTTR (dk)'

print('=== DÜZELTILMIŞ MTTR HESAPLAMASI ===\n')

mttr_values = []

# Excel verisi "120 dk", "61 dk" gibi string formatında olabilir
for val in df[mttr_col].dropna():
    try:
        val_str = str(val).strip()
        print(f"İşleniyor: '{val_str}'", end=" ")
        
        # Metin içinden sayıyı çıkar (regex)
        match = re.search(r'(\d+(?:[\.,]\d+)?)', val_str)
        if match:
            number_str = match.group(1).replace(',', '.')
            number = float(number_str)
            mttr_values.append(number)
            print(f"→ {number}")
        else:
            print(f"→ HATA: Sayı bulunamadı")
    except Exception as e:
        print(f"→ HATA: {e}")

print(f'\nToplam çıkarılan değer: {len(mttr_values)}')

if len(mttr_values) > 0:
    mttr_minutes = sum(mttr_values) / len(mttr_values)
    mttr_minutes = round(mttr_minutes, 1)
    
    hours = int(mttr_minutes // 60)
    minutes = int(mttr_minutes % 60)
    mttr_formatted = f"{hours}h {minutes}m"
    
    print(f'\n✅ Ortalama MTTR: {mttr_minutes} dakika')
    print(f'✅ Formatlanmış: {mttr_formatted}')
    print(f'✅ Saat cinsinden: {round(mttr_minutes / 60, 1)} saat')
else:
    print('\n❌ MTTR verisi bulunamadı!')
