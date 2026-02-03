#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FRACAS analiz fonksiyonlarını test et
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from flask import Flask
from app import create_app
from routes.fracas import (
    calculate_basic_stats,
    calculate_rams_metrics,
    calculate_pareto_analysis,
    calculate_trend_analysis,
    calculate_supplier_analysis,
    calculate_cost_analysis,
    get_column
)

# Flask uygulaması oluştur
app = create_app()

# Veri yükleme fonksiyonu (Flask context olmadan)
def load_fracas_data_direct():
    """Excel'den FRACAS verilerini yükle (Flask context olmadan)"""
    current_project = 'belgrad'
    project_folder = os.path.join(app.root_path, 'data', current_project)
    
    if not os.path.exists(project_folder):
        return None
    
    # FRACAS dosyasını bul
    for filename in os.listdir(project_folder):
        if 'fracas' in filename.lower() and filename.endswith(('.xlsx', '.xls')) and not filename.startswith('~$'):
            excel_path = os.path.join(project_folder, filename)
            try:
                df = pd.read_excel(excel_path, sheet_name='FRACAS', header=0)
                df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
                
                fracas_col = None
                for col in df.columns:
                    if 'fracas' in col.lower() and 'id' in col.lower():
                        fracas_col = col
                        break
                if fracas_col:
                    df = df[df[fracas_col].notna()]
                
                return df
            except Exception as e:
                print(f"Excel okuma hatası: {e}")
                return None
    return None

# Test: Veri yükleme
print("=" * 80)
print("FRACAS ANALIZ FONKSİYONLARI TEST")
print("=" * 80)

print("\n1. Excel verisi yükleniyor...")
df = load_fracas_data_direct()

if df is None:
    print("❌ Excel yüklenemedi!")
    sys.exit(1)

print(f"✓ Excel yüklendi: {len(df)} satır")
print(f"✓ Sütunlar ({len(df.columns)}): {list(df.columns[:10])}...")

# Test: Kolon bulma
print("\n2. Kolon eşleştirmeleri kontrol ediliyor...")
vehicle_col = get_column(df, ['araç numarası', 'tram_id'])
module_col = get_column(df, ['sistem', 'araç modülü'])
supplier_col = get_column(df, ['ilgili tedarikçi', 'tedarikçi'])
repair_col = get_column(df, ['tamir süresi (dakika)', 'tamir süresi'])

print(f"  Araç Numarası sütunu: {vehicle_col}")
print(f"  Sistem/Modül sütunu: {module_col}")
print(f"  Tedarikçi sütunu: {supplier_col}")
print(f"  Tamir Süresi sütunu: {repair_col}")

if not vehicle_col or not module_col:
    print("❌ Gerekli sütunlar bulunamadı!")
    print("\nMevcut tüm sütunlar:")
    for i, col in enumerate(df.columns):
        print(f"  {i}: {col}")
    sys.exit(1)

# Test: Temel istatistikler
print("\n3. Temel İstatistikler...")
try:
    stats = calculate_basic_stats(df)
    print(f"  ✓ Toplam arızalar: {stats.get('total_failures', 0)}")
    print(f"  ✓ Unique araçlar: {stats.get('unique_vehicles', 0)}")
    print(f"  ✓ Unique modüller: {stats.get('unique_modules', 0)}")
    print(f"  ✓ Unique tedarikçiler: {stats.get('total_suppliers', 0)}")
    print(f"  ✓ Garanti talepleri: {stats.get('warranty_claims', 0)}")
except Exception as e:
    print(f"  ❌ Hata: {e}")

# Test: RAMS Metrikleri
print("\n4. RAMS Metrikleri...")
try:
    rams = calculate_rams_metrics(df)
    print(f"  ✓ MTBF: {rams.get('mtbf')}")
    print(f"  ✓ MTTR (dk): {rams.get('mttr')}")
    print(f"  ✓ MDT (dk): {rams.get('mdt')}")
    print(f"  ✓ MWT (dk): {rams.get('mwt')}")
    print(f"  ✓ Availability: {rams.get('availability')}%")
    print(f"  ✓ Reliability: {rams.get('reliability')}%")
except Exception as e:
    print(f"  ❌ Hata: {e}")

# Test: Pareto Analizi
print("\n5. Pareto Analizi...")
try:
    pareto = calculate_pareto_analysis(df)
    print(f"  ✓ Top modüller: {len(pareto['by_module'])} item")
    if pareto['by_module']:
        print(f"    - En çok: {pareto['by_module'][0]['name']} ({pareto['by_module'][0]['count']} arıza)")
    print(f"  ✓ Top tedarikçiler: {len(pareto['by_supplier'])} item")
    if pareto['by_supplier']:
        print(f"    - En çok: {pareto['by_supplier'][0]['name']} ({pareto['by_supplier'][0]['count']} arıza)")
    print(f"  ✓ Lokasyonlar: {len(pareto['by_location'])} item")
    print(f"  ✓ Arıza sınıfları: {len(pareto['by_failure_class'])} item")
except Exception as e:
    print(f"  ❌ Hata: {e}")

# Test: Trend Analizi
print("\n6. Trend Analizi...")
try:
    trend = calculate_trend_analysis(df)
    print(f"  ✓ Aylık trend: {len(trend['monthly'])} ay")
    print(f"  ✓ Saatlik dağılım: {len(trend['by_hour'])} saat")
    print(f"  ✓ Haftalık dağılım: {len(trend['by_weekday'])} gün")
except Exception as e:
    print(f"  ❌ Hata: {e}")

# Test: Tedarikçi Analizi
print("\n7. Tedarikçi Performans Analizi...")
try:
    supplier = calculate_supplier_analysis(df)
    print(f"  ✓ Tedarikçiler: {len(supplier['performance'])} item")
    if supplier['performance']:
        for i, supp in enumerate(supplier['performance'][:3]):
            print(f"    {i+1}. {supp['name']}: {supp['failure_count']} arıza")
except Exception as e:
    print(f"  ❌ Hata: {e}")

# Test: Maliyet Analizi
print("\n8. Maliyet Analizi...")
try:
    cost = calculate_cost_analysis(df)
    print(f"  ✓ Toplam malzeme: {cost.get('total_material', 0)} ₺")
    print(f"  ✓ Toplam işçilik: {cost.get('total_labor', 0)} ₺")
    print(f"  ✓ Toplam maliyet: {cost.get('total_cost', 0)} ₺")
except Exception as e:
    print(f"  ❌ Hata: {e}")

print("\n" + "=" * 80)
print("TEST TAMAMLANDI")
print("=" * 80)
