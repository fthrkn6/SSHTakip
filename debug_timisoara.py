import pandas as pd
from datetime import datetime, timedelta
import os

project = 'timisoara'
ariza_dir = f'logs/{project}/ariza_listesi'

# FRACAS dosyasını bul
fracas_file = None
if os.path.exists(ariza_dir):
    for file in os.listdir(ariza_dir):
        if 'fracas' in file.lower() and file.endswith('.xlsx'):
            fracas_file = os.path.join(ariza_dir, file)
            break

print(f"=== {project.upper()} - FRACAS DOSYASI DETAY ===\n")
print(f"Dosya: {fracas_file}\n")

# Excel oku
df = pd.read_excel(fracas_file, sheet_name='FRACAS', header=3)

print(f"Toplam satır: {len(df)}")
print(f"\nSütunlar:")
for i, col in enumerate(df.columns):
    print(f"{i}: {repr(col)}")

# Arıza sınıfı sütunu bul
print(f"\n\n=== ARIZA SINIFI SÜTUNU ARAMA ===")
sinif_col = None
for col in df.columns:
    if 'arıza' in col.lower() and 'sınıf' in col.lower():
        print(f"BULUNDU: {repr(col)}")
        sinif_col = col
        break

if not sinif_col:
    print("BULUNAMADI!")
    # Manuel ara
    print("\nManuel arama:")
    for col in df.columns:
        if 'failure' in col.lower() or 'sinif' in col.lower() or 'class' in col.lower():
            print(f"  Alternatif: {repr(col)}")

print(f"\n\n=== SÜTÜN İÇERİĞİ ===")
if sinif_col:
    print(f"Sütun: {repr(sinif_col)}")
    print(f"\nİlk 20 değer:")
    print(df[sinif_col].head(20).to_string())
    
    print(f"\n\nValue counts:")
    vc = df[sinif_col].value_counts()
    print(vc)
    
    print(f"\n\n=== SINIFLARA GÖRE SAY ===")
    counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    for sinif in df[sinif_col].dropna():
        sinif_str = str(sinif).strip()
        print(f"  '{sinif_str}' → ", end="")
        if sinif_str.startswith('A'):
            counts['A'] += 1
            print("A")
        elif sinif_str.startswith('B'):
            counts['B'] += 1
            print("B")
        elif sinif_str.startswith('C'):
            counts['C'] += 1
            print("C")
        elif sinif_str.startswith('D'):
            counts['D'] += 1
            print("D")
        else:
            print("??")
    
    print(f"\nSayılar:")
    print(f"A: {counts['A']}")
    print(f"B: {counts['B']}")
    print(f"C: {counts['C']}")
    print(f"D: {counts['D']}")
    print(f"Toplam: {sum(counts.values())}")

# Tarih sütununu da kontrol et
print(f"\n\n=== TARİH SÜTUNU ===")
tarih_col = None
for col in df.columns:
    if 'tarih' in col.lower() and 'hata' in col.lower():
        tarih_col = col
        break

if tarih_col:
    print(f"Bulundu: {repr(tarih_col)}")
    print(f"\nİlk 10 değer:")
    print(df[tarih_col].head(10).to_string())
    
    print(f"\n\nDatum dönüştürme:")
    df[tarih_col] = pd.to_datetime(df[tarih_col], errors='coerce')
    
    print(f"Min: {df[tarih_col].min()}")
    print(f"Max: {df[tarih_col].max()}")
    
    last_30_days = datetime.utcnow() - timedelta(days=30)
    print(f"Son 30 gün başlangıcı: {last_30_days}")
    
    filtered = df[df[tarih_col] >= last_30_days]
    print(f"\nSon 30 günde: {len(filtered)} arıza")
else:
    print("Bulunamadı!")
