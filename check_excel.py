"""Excel'deki arıza verileri kontrol et"""
import pandas as pd
import os

belgrad_path = r'data/belgrad/Veriler.xlsx'

print(f"Checking: {belgrad_path}")
print(f"Exists: {os.path.exists(belgrad_path)}\n")

if os.path.exists(belgrad_path):
    try:
        # Excel'i oku
        df = pd.read_excel(belgrad_path, sheet_name='Sayfa2')
        print(f"Satır sayısı: {len(df)}")
        print(f"Sütun sayısı: {len(df.columns)}")
        print(f"\nSütunlar: {list(df.columns)}\n")
        
        # tram_id bul
        tram_id_col = None
        for col in df.columns:
            if 'tram' in col.lower() and 'id' in col.lower():
                tram_id_col = col
                print(f"✓ tram_id sütunu bulundu: '{col}'")
                break
        
        # Arıza sınıfı bul
        ariza_col = None
        for col in df.columns:
            if 'arız' in col.lower() or 'class' in col.lower():
                ariza_col = col
                print(f"✓ Arıza sütunu bulundu: '{col}'")
                break
        
        # Sistem/Module bul
        sistem_col = None
        for col in df.columns:
            if 'module' in col.lower() or 'sistem' in col.lower():
                sistem_col = col
                print(f"✓ Sistem sütunu bulundu: '{col}'")
                break
        
        if tram_id_col and ariza_col:
            print(f"\n[İlk 5 satır]")
            for idx, row in df.head(5).iterrows():
                tram = str(row.get(tram_id_col, '')).strip()
                ariza = str(row.get(ariza_col, '')).strip()
                sistem = str(row.get(sistem_col, 'N/A')).strip() if sistem_col else 'N/A'
                
                if ariza != 'nan':
                    print(f"  Tramvay: {tram}, Arıza: {ariza}, Sistem: {sistem}")
        
        # Arıza dolu satırları say
        if ariza_col:
            non_null = df[ariza_col].notna().sum()
            print(f"\nArıza sütununda dolu satır: {non_null}")
            
    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()
