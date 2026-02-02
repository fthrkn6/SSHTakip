import os
import sys

# Direkt test - app import etmeden
os.chdir('c:\\Users\\ferki\\Desktop\\bozankaya_ssh_takip\\data\\belgrad')

import pandas as pd

# FRACAS dosyasını bul
fracas_file = [f for f in os.listdir('.') if 'fracas' in f.lower() and f.endswith('.xlsx')][0]
print(f"✅ Dosya bulundu: {fracas_file}\n")

# Excel'i oku
df = pd.read_excel(fracas_file, sheet_name='FRACAS', header=3)
df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()

print(f"✅ Toplam arıza kaydı: {len(df)}")
print(f"✅ Sütunlar: {list(df.columns)[:8]}\n")

# FRACAS ID kolonunu bul
fracas_col = None
for col in df.columns:
    if 'fracas' in col.lower() and 'id' in col.lower():
        fracas_col = col
        break

if fracas_col:
    print(f"✅ FRACAS ID kolonu bulundu: {fracas_col}")
    df = df[df[fracas_col].notna()]
    print(f"✅ Boş satırlardan sonra: {len(df)} kayıt")
else:
    print("❌ FRACAS ID kolonu bulunamadı")
    print(f"Mevcut kolonlar: {list(df.columns)}")

# İlk 3 kaydı göster
print(f"\n=== İlk 3 Arıza Kaydı ===")
for i, (_, row) in enumerate(df.head(3).iterrows()):
    print(f"\n{i+1}. Kaydı:")
    print(f"   FRACAS ID: {row.get(fracas_col, 'N/A')}")
    print(f"   Araç: {row.get('Araç Numarası  Vehicle Number', 'N/A')}")
    print(f"   Açıklama: {row.get('Açıklama', 'N/A')}")
