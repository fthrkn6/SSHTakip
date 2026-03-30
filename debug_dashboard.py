import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Kayseri projesi için test et
current_project = 'belgrad'
ariza_dir = f'logs/{current_project}/ariza_listesi'

# FRACAS dosyasını bul
ariza_listesi_file = None
for file in os.listdir(ariza_dir):
    if 'fracas' in file.lower() and file.endswith('.xlsx'):
        ariza_listesi_file = os.path.join(ariza_dir, file)
        break

print(f"Dosya: {ariza_listesi_file}\n")

# Header row'u belirle
header_row = 3 if 'logs' in ariza_listesi_file and 'ariza_listesi' in ariza_listesi_file else 0
df = pd.read_excel(ariza_listesi_file, sheet_name='FRACAS', header=header_row)

print("=== TÜM SÜTUNLAR ===")
for i, col in enumerate(df.columns):
    print(f"{i}: {repr(col)}")

print("\n=== TARIH SÜTUNU ===")
# Tarih sütununu bul
tarih_col = None
for col in df.columns:
    if 'tarih' in col.lower() and 'hata' in col.lower():
        tarih_col = col
        print(f"Bulunan: {repr(tarih_col)}")
        break

print(f"\nTarih sütunu: {tarih_col}")
print(f"İlk 10 değer:\n{df[tarih_col].head(10)}")

print("\n=== ARIZA SINIFI SÜTUNU (TAM İSİM) ===")
# Arıza sınıfı sütununu bul
sinif_col = None
for col in df.columns:
    if 'arıza' in col.lower() and 'sınıf' in col.lower():
        sinif_col = col
        print(f"Bulunan: {repr(sinif_col)}")
        break

if sinif_col:
    print(f"\nSınıf sütunu: {repr(sinif_col)}")
    print("İlk 30 değer:")
    print(df[sinif_col].head(30))
    print(f"\nValue counts:")
    print(df[sinif_col].value_counts())

print("\n=== SON 30 GÜN FİLTRESİ ===")
if tarih_col:
    df[tarih_col] = pd.to_datetime(df[tarih_col], errors='coerce')
    last_30_days = datetime.utcnow() - timedelta(days=30)
    print(f"Bugünkü tarih: {datetime.utcnow()}")
    print(f"Son 30 gün başlangıcı: {last_30_days}")
    
    df_filtered = df[df[tarih_col] >= last_30_days]
    print(f"\nToplam satır: {len(df)}")
    print(f"Son 30 gündeki satır: {len(df_filtered)}")
    
    if sinif_col and len(df_filtered) > 0:
        print(f"\nSon 30 gündeki sınıf dağılımı:")
        print(df_filtered[sinif_col].value_counts())
        
        # Her sınıftan kaçar tane
        counts = {
            'A': 0, 'B': 0, 'C': 0, 'D': 0
        }
        for sinif in df_filtered[sinif_col].dropna():
            sinif_str = str(sinif).strip()
            if sinif_str.startswith('A'):
                counts['A'] += 1
            elif sinif_str.startswith('B'):
                counts['B'] += 1
            elif sinif_str.startswith('C'):
                counts['C'] += 1
            elif sinif_str.startswith('D'):
                counts['D'] += 1
        print(f"\nSınıflandırılan sayılar (A/B/C/D):")
        print(counts)
        print(f"Toplam: {sum(counts.values())}")
