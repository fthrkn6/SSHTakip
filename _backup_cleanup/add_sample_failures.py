"""Excel'e araçlara örnek arıza verisi ekle"""
import pandas as pd
import os

excel_path = 'data/belgrad/Veriler.xlsx'
df = pd.read_excel(excel_path, sheet_name='Sayfa2', header=0)

print(f'Mevcut satır: {len(df)}\n')

# Son 5 araçlara (1551-1555) örnek arıza verisi ekle
sample_ariza_sinifi = [
    'A-Kritik/Emniyet Riski',
    'B-Yüksek/Operasyon Engeller',
    'C-Hafif/Kısıtlı Operasyon',
    'D-Arıza Değildir'
]

sample_ariza_kaynagi = [
    'Bozankaya',
    'Tedarikçi',
    'Müşteri',
    'İç Sebepler'
]

# 1551-1555 araçlarına veri ekle (sıfırdan başlarsak index 20-24)
for i in range(20, 25):
    if i < len(df):
        df.at[i, 'Arıza Sınıfı '] = sample_ariza_sinifi[i % len(sample_ariza_sinifi)]
        df.at[i, 'Arıza Kaynağı'] = sample_ariza_kaynagi[i % len(sample_ariza_kaynagi)]

print('Güncellenen verileri:')
print(df[['tram_id', 'Arıza Sınıfı ', 'Arıza Kaynağı']].tail(10).to_string(index=False))

# Kaydet
df.to_excel(excel_path, sheet_name='Sayfa2', index=False)
print(f'\n✓ Excel güncellendi: {excel_path}')
