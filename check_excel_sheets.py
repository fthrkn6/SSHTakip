#!/usr/bin/env python
"""
Excel Sayfa 2'den tram_id verilerini çek
"""
import pandas as pd
import os

def check_excel_sheets():
    """Excel dosyasının tüm sheet'lerini kontrol et"""
    excel_path = 'data/belgrad/BEL25_FRACAS.xlsx'
    
    if os.path.exists(excel_path):
        try:
            # Tüm sheet'leri oku
            xls = pd.ExcelFile(excel_path)
            print(f"📊 Excel dosyası: {excel_path}")
            print(f"Sheet'ler: {xls.sheet_names}")
            
            # Her sheet'i kontrol et
            for sheet_name in xls.sheet_names:
                print(f"\n{'='*60}")
                print(f"📄 Sheet: {sheet_name}")
                print(f"{'='*60}")
                
                df = pd.read_excel(excel_path, sheet_name=sheet_name, header=0, engine='openpyxl')
                
                print(f"Sütunlar: {list(df.columns)}")
                print(f"Satırlar: {len(df)}")
                
                # Sütunları temizle
                df.columns = df.columns.astype(str).str.replace('\n', ' ', regex=False).str.strip()
                
                # tram_id, Araç Numarası, Equipment ID vs. arayabilecek sütunları bul
                tram_columns = [col for col in df.columns if 'tram' in col.lower() or 'araç' in col.lower() or 'equipment' in col.lower() or 'id' in col.lower()]
                
                if tram_columns:
                    print(f"\n✅ Tramvay ile ilgili sütunlar: {tram_columns}")
                    for col in tram_columns:
                        print(f"\n   📋 {col}")
                        print(f"   Benzersiz değerler: {df[col].dropna().nunique()}")
                        print(f"   İlk 5 değer: {df[col].dropna().head(5).tolist()}")
                else:
                    print("❌ Tramvay ile ilgili sütun bulunamadı")
                
                # İlk 3 satırı göster
                print(f"\nİlk 3 satır:")
                print(df.head(3).to_string())
        
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Excel bulunamadı: {excel_path}")

if __name__ == '__main__':
    check_excel_sheets()
