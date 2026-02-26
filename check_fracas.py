"""Fracas_BELGRAD.xlsx dosyasını kontrol et"""
import pandas as pd
import os

fracas_file = r'logs/belgrad/ariza_listesi/Fracas_BELGRAD.xlsx'

print(f"Checking: {fracas_file}")
print(f"Exists: {os.path.exists(fracas_file)}\n")

if os.path.exists(fracas_file):
    try:
        # Sheet'leri listele
        xl = pd.ExcelFile(fracas_file)
        print(f"Sheets: {xl.sheet_names}\n")
        
        # FRACAS sheet'ini oku - header row 3 (index 3)
        df = pd.read_excel(fracas_file, sheet_name='FRACAS', header=3)
        print(f"Satır: {len(df)}")
        print(f"Sütun: {len(df.columns)}")
        print(f"\nSütunlar: {list(df.columns)}\n")
        
        # tram_id, arıza sınıfı gibi sütunları bul
        tram_col = None
        ariza_col = None
        sistem_col = None
        
        for col in df.columns:
            if 'tram' in col.lower() and 'id' in col.lower():
                tram_col = col
            if 'arız' in col.lower():
                ariza_col = col
            if 'module' in col.lower() or 'sistem' in col.lower():
                sistem_col = col
        
        print(f"tram_id sütunu: {tram_col}")
        print(f"Arıza sütunu: {ariza_col}")
        print(f"Sistem sütunu: {sistem_col}\n")
        
        # Arıza dolu satırları say
        if ariza_col:
            non_null = df[ariza_col].notna().sum()
            print(f"Arıza dolu satır: {non_null}\n")
            
            # İlk 5 arızayı göster
            print("İlk 5 arıza:")
            ariza_df = df[df[ariza_col].notna()].head(5)
            for idx, row in ariza_df.iterrows():
                tram = row.get(tram_col, 'N/A') if tram_col else 'N/A'
                ariza = row.get(ariza_col, 'N/A')
                sistem = row.get(sistem_col, 'N/A') if sistem_col else 'N/A'
                print(f"  Tramvay: {tram}, Arıza: {ariza}, Sistem: {sistem}")
        
    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()
