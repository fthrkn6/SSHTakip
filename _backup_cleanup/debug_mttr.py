#!/usr/bin/env python3
"""MTTR hesaplamasını debug etmek için"""

import pandas as pd
import os

filepath = r'c:\Users\ferki\Desktop\bozankaya_ssh_takip\logs\belgrad\ariza_listesi\Ariza_Listesi_BELGRAD.xlsx'

df = pd.read_excel(filepath, sheet_name='Ariza Listesi', header=3)

print('=== MTTR SÜTUNU ANALİZİ ===')
print(f'Toplam satır: {len(df)}')
print(f'\nMTTR (dk) sütunu:')
print(f'  Boş olmayan: {df["MTTR (dk)"].notna().sum()}')
print(f'  Boş: {df["MTTR (dk)"].isna().sum()}')

# Sayısal dönüşüm yap
mttr_numeric = pd.to_numeric(df['MTTR (dk)'], errors='coerce')
print(f'  Sayısal dönüştürme sonrası boş: {mttr_numeric.isna().sum()}')
print(f'  Sayısal dönüştürme sonrası dolu: {mttr_numeric.notna().sum()}')

# İlk 10 değeri göster
print(f'\nİlk 10 MTTR (dk) değeri:')
for i, val in enumerate(df['MTTR (dk)'].head(10), 1):
    print(f'  {i}. {repr(val)} (type: {type(val).__name__})')

# İstatistikler
mttr_clean = mttr_numeric.dropna()
if len(mttr_clean) > 0:
    print(f'\nMTTR İstatistikleri:')
    print(f'  Ortalama: {mttr_clean.mean():.1f} dakika')
    print(f'  Min: {mttr_clean.min():.1f}')
    print(f'  Max: {mttr_clean.max():.1f}')
    print(f'  Std Dev: {mttr_clean.std():.1f}')
    
    # Saat:dakika formatına dönüştür
    avg_minutes = mttr_clean.mean()
    hours = int(avg_minutes // 60)
    minutes = int(avg_minutes % 60)
    print(f'\nFormatlı: {hours}h {minutes}m')
else:
    print('MTTR verisi bulunamadı!')

# Tüm sütunları listele
print(f'\n=== TÜÜMM SÜTUNLAR ===')
for i, col in enumerate(df.columns, 1):
    print(f'{i}. {col}')
