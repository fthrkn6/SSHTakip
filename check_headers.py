import pandas as pd
import os

os.chdir('data/belgrad')

# Dosya adını bul
fracas_file = [f for f in os.listdir('.') if 'fracas' in f.lower() and f.endswith('.xlsx')][0]
print(f"Dosya: {fracas_file}\n")

# Farklı header seçeneklerini deneyelim
for header_row in [0, 1, 2, 3, 4]:
    try:
        df = pd.read_excel(fracas_file, sheet_name='FRACAS', header=header_row)
        print(f"\n=== Header satırı {header_row} ===")
        print(f"Kolonlar: {list(df.columns)[:5]}")  # İlk 5 kolonu göster
        print(f"Shape: {df.shape}")
        print(f"İlk satır: {df.iloc[0][:5] if len(df) > 0 else 'Boş'}")
    except Exception as e:
        print(f"Header {header_row} hatası: {e}")
