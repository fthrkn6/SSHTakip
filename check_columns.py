import os
import pandas as pd

os.chdir('c:\\Users\\ferki\\Desktop\\bozankaya_ssh_takip\\data\\belgrad')

# FRACAS dosyasını bul
fracas_file = [f for f in os.listdir('.') if 'fracas' in f.lower() and f.endswith('.xlsx')][0]

# Excel'i oku
df = pd.read_excel(fracas_file, sheet_name='FRACAS', header=3)
df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()

print("=== EXCEL SÜTUNLARI ===\n")
for i, col in enumerate(df.columns, 1):
    print(f"{i:2}. {col}")

print(f"\n=== İLK KAYIT VERİSİ ===\n")
first_row = df.iloc[0]
for col in df.columns:
    val = first_row.get(col, 'N/A')
    if pd.notna(val) and str(val).strip() and str(val) != 'nan':
        print(f"{col}: {val}")
