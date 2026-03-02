import pandas as pd
import os

# Kayseri Veriler.xlsx kontrol
kayseri_excel = 'data/kayseri/Veriler.xlsx'
if os.path.exists(kayseri_excel):
    df = pd.read_excel(kayseri_excel, sheet_name='Sayfa2', header=0, engine='openpyxl')
    print(f"Kayseri Sayfa2 sütunları: {list(df.columns)[:10]}")
    print(f"\nKayseri Sayfa2 - İlk 10 satır:")
    print(df.iloc[:10, 0:3].to_string())
    print(f"\nToplam satır: {len(df)}")
    
    # Araç kodlarını göster
    first_col = df.columns[0]
    print(f"\nBirinci sütundaki araç kodları: {df[first_col].unique()}")
else:
    print(f"File not found: {kayseri_excel}")
