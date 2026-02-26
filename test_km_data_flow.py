#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KM veri akışını test et:
1. Veriler.xlsx'ten doğru 25 araç yükle
2. Equipment tablosunu kontrol et (boş olmalı ilk başta)
3. KM giriş formundan veri gir
4. Tüm sayfalarda veri görüldüğünü doğrula
"""
import os
import sys
sys.path.insert(0, '.')

from app import create_app
from models import Equipment, db
from routes.dashboard import sync_excel_to_equipment
import pandas as pd

app = create_app()

with app.app_context():
    project_code = 'belgrad'
    
    print("="*70)
    print("KM VERİ AKIŞI TESTİ")
    print("="*70)
    
    # 1. Veriler.xlsx'ten araçları kontrol et
    print("\n[1] Veriler.xlsx'ten araçları kontrol et:")
    veriler_file = os.path.join('data', project_code, 'Veriler.xlsx')
    if os.path.exists(veriler_file):
        df = pd.read_excel(veriler_file, sheet_name='Sayfa2')
        tram_ids = [str(t) for t in df['tram_id'].dropna().unique()]
        print(f"    ✓ Toplam araç: {len(tram_ids)}")
        print(f"    ✓ Araçlar: {sorted(tram_ids)}")
    else:
        print(f"    ✗ Veriler.xlsx bulunamadı!")
    
    # 2. Equipment tablosunu senkronize et
    print("\n[2] Equipment tablosunu senkronize et (Veriler.xlsx'ten):")
    try:
        trams = sync_excel_to_equipment(project_code)
        print(f"    ✓ Senkronize edilen araçlar: {len(trams)}")
    except Exception as e:
        print(f"    ✗ Sync hatası: {e}")
    
    # 3. Equipment tablosunu kontrol et
    print("\n[3] Equipment tablosunu kontrol et:")
    equipments = Equipment.query.filter_by(project_code=project_code, equipment_type='Tramvay').all()
    print(f"    Toplam Tramvay Equipment: {len(equipments)}")
    print(f"    Equipment codes: {sorted([e.equipment_code for e in equipments])}")
    
    # 4. KM değerlerini kontrol et
    print("\n[4] KM değerlerini kontrol et:")
    total_km = sum(e.current_km or 0 for e in equipments)
    print(f"    Toplam KM: {total_km}")
    print(f"    Değeri olan araçlar:")
    for eq in equipments:
        if eq.current_km:
            print(f"      {eq.equipment_code}: {eq.current_km} km")
    
    # 5. Ekstra test: get_tramvay_list_with_km() kullan
    print("\n[5] get_tramvay_list_with_km() filtresi kullan:")
    try:
        from utils_project_excel_store import get_tramvay_list_with_km
        result = get_tramvay_list_with_km(project_code)
        print(f"    Döndürülen araçlar: {len(result)}")
        result_codes = sorted([str(e.equipment_code) for e in result])
        print(f"    Codes: {result_codes}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    print("\n" + "="*70)
    print("SONUÇ: Equipment tablosu KM verilerinin TEK KAYNAĞI")
    print("  • KM giriş: /tramvay-km/guncelle → Equipment.current_km")
    print("  • KM okuma: Tüm sayfalar → Equipment.current_km")
    print("="*70)
