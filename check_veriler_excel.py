#!/usr/bin/env python
"""
Veriler.xlsx dosyasının sayfa 2'sini kontrol et
"""
import pandas as pd
import os

def check_veriler_excel():
    """Veriler.xlsx'in tüm sheet'lerini kontrol et"""
    excel_path = 'Veriler.xlsx'
    
    if os.path.exists(excel_path):
        try:
            # Tüm sheet'leri oku
            xls = pd.ExcelFile(excel_path)
            print(f"📊 Excel dosyası: {excel_path}")
            print(f"📄 Sheet'ler: {xls.sheet_names}\n")
            
            # Her sheet'i kontrol et
            for i, sheet_name in enumerate(xls.sheet_names):
                print(f"{'='*70}")
                print(f"Sheet {i}: {sheet_name}")
                print(f"{'='*70}")
                
                df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None, engine='openpyxl')
                
                print(f"Boyut: {df.shape[0]} satır x {df.shape[1]} sütun\n")
                
                # İlk 10 satırı göster
                print("İlk 10 satır:")
                print(df.head(10).to_string())
                print("\n")
        
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Dosya bulunamadı: {excel_path}")
        print("Mevcut dosyalar:")
        for f in os.listdir('.'):
            if f.endswith('.xlsx'):
                print(f"  - {f}")

if __name__ == '__main__':
    check_veriler_excel()
