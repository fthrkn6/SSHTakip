#!/usr/bin/env python
"""
data/belgrad/Veriler.xlsx dosyasını kontrol et
"""
import pandas as pd
import os

def check_veriler_excel():
    """Veriler.xlsx'in tüm sheet'lerini kontrol et"""
    excel_path = 'data/belgrad/Veriler.xlsx'
    
    if os.path.exists(excel_path):
        try:
            # Tüm sheet'leri oku
            xls = pd.ExcelFile(excel_path)
            print(f"📊 Excel dosyası: {excel_path}")
            print(f"📄 Sheet'ler: {xls.sheet_names}\n")
            
            # Sayfa 2'yi kontrol et (index 1)
            if len(xls.sheet_names) > 1:
                sheet_name = xls.sheet_names[1]
                print(f"{'='*70}")
                print(f"Sheet 2: {sheet_name}")
                print(f"{'='*70}\n")
                
                df = pd.read_excel(excel_path, sheet_name=sheet_name, header=0, engine='openpyxl')
                
                print(f"Sütunlar: {list(df.columns)}")
                print(f"Satırlar: {len(df)}\n")
                
                # tram_id sütununu bul
                tram_col = None
                for col in df.columns:
                    if 'tram' in col.lower() or 'id' in col.lower() or 'araç' in col.lower():
                        tram_col = col
                        break
                
                if tram_col:
                    print(f"✅ Bulunan tram_id sütunu: {tram_col}")
                    tram_ids = df[tram_col].dropna().unique()
                    print(f"Benzersiz tramvaylar: {len(tram_ids)}")
                    print(f"Tramvaylar: {tram_ids}\n")
                
                # İlk 10 satırı göster
                print("İlk 10 satır:")
                print(df.head(10).to_string())
            else:
                print("❌ Sayfa 2 bulunamadı")
        
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Dosya bulunamadı: {excel_path}")

if __name__ == '__main__':
    check_veriler_excel()
