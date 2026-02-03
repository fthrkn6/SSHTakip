#!/usr/bin/env python
"""
Excel'den tram_id verilerini çek
"""
import pandas as pd
from app import create_app, db
from models import Equipment
import os

def load_tram_ids_from_excel():
    """Excel dosyasından tram_id'leri oku"""
    app = create_app()
    
    with app.app_context():
        # Excel dosyasını bul
        excel_paths = [
            'data/belgrad/BEL25_FRACAS.xlsx',
            'data/gebze/GEB25_FRACAS.xlsx',
            'data/iasi/ISI25_FRACAS.xlsx',
        ]
        
        all_tram_ids = set()
        
        for excel_path in excel_paths:
            if os.path.exists(excel_path):
                try:
                    df = pd.read_excel(excel_path, sheet_name='FRACAS', header=0, engine='openpyxl')
                    
                    print(f"\n📊 {excel_path}")
                    print(f"Sütunlar: {list(df.columns)}")
                    
                    # Araç Numarası sütununu bul
                    for col in df.columns:
                        if 'araç' in col.lower() or 'numarası' in col.lower() or 'equipment' in col.lower():
                            print(f"\n✅ Bulunan sütun: {col}")
                            tram_ids = df[col].dropna().unique()
                            print(f"Tramvaylar: {tram_ids}")
                            all_tram_ids.update(tram_ids)
                            break
                    
                    # İlk birkaç satırı göster
                    print(f"\nİlk 3 satır:")
                    print(df.head(3))
                    
                except Exception as e:
                    print(f"❌ Hata: {str(e)}")
        
        print(f"\n🚊 Toplam benzersiz tramvay: {len(all_tram_ids)}")
        print(f"Tramvaylar: {sorted(all_tram_ids)}")

if __name__ == '__main__':
    load_tram_ids_from_excel()
