import pandas as pd
import os

veriler_path = "data/belgrad/Veriler.xlsx"

if os.path.exists(veriler_path):
    print("=" * 70)
    print("VERILER.XLSX İÇERİĞİ")
    print("=" * 70)
    
    # Tüm sheet'leri oku
    xls = pd.ExcelFile(veriler_path)
    print(f"\nSheet'ler: {xls.sheet_names}\n")
    
    # Sayfa1 - Sistem yapısı
    print("--- SAYFA1 (İlk 10 satır) ---")
    df1 = pd.read_excel(veriler_path, sheet_name='Sayfa1', header=None)
    print(df1.head(10))
    print(f"Shape: {df1.shape}")
    
    # Sayfa2 - Tramvay verileri
    print("\n" + "=" * 70)
    print("--- SAYFA2 (İlk 15 satır) ---")
    df2 = pd.read_excel(veriler_path, sheet_name='Sayfa2')
    print(f"Sütunlar: {list(df2.columns)}")
    print(df2.head(15))
    print(f"Shape: {df2.shape}")
    
    # tram_id sütununu ara
    print("\n" + "=" * 70)
    print("--- TRAM_ID ARAŞTIRMASI ---")
    for col in df2.columns:
        col_lower = col.lower()
        if 'tram' in col_lower or 'arac' in col_lower or 'id' in col_lower:
            print(f"\nSütun: '{col}'")
            print(df2[col].head(10).tolist())
else:
    print("Veriler.xlsx bulunamadı!")
