import pandas as pd
import os

# Timisoara Veriler.xlsx kontrol
timisoara_excel = 'data/timisoara/Veriler.xlsx'
if os.path.exists(timisoara_excel):
    df = pd.read_excel(timisoara_excel, sheet_name='Sayfa2', header=0, engine='openpyxl')
    
    first_col = df.columns[0]
    print(f"Timisoara araç kodları: {sorted(df[first_col].unique())}")
    print(f"\nToplam araç: {len(df)}")
    
    # 4001 var mı?
    if 4001 in df[first_col].values:
        print("✓ 4001 Timisoara'da bulundu")
    else:
        print("✗ 4001 Timisoara'da BULUNAMADI")
else:
    print(f"File not found: {timisoara_excel}")
