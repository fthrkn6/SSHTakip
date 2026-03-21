#!/usr/bin/env python3
"""Test rapor sistemi - Verilen fonksiyonlarla"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.reports import (
    get_fracas_data, filter_by_period, get_vehicle_analysis, 
    get_system_analysis, get_supplier_system_matrix, 
    create_management_pdf, PROJECTS, PERIODS
)
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

print("\n" + "="*60)
print("RAPOR SISTEMI TEST")
print("="*60 + "\n")

# Test 1: Proje verilerini yükle
all_projects = ['BELGRAD', 'ISTANBUL', 'KAYSERI']
print("[TEST 1] Verileri yüklüyor...")

for proj in all_projects:
    data = get_fracas_data(proj)
    if data is not None and not data.empty:
        print(f"  ✓ {proj}: {len(data)} kayıt")
    else:
        print(f"  ✗ {proj}: Veri yok")

# Test 2: Belgrad için rapor oluştur
print("\n[TEST 2] Belgrad için rapor oluşturuyor...")
project = 'BELGRAD'
fracas_df = get_fracas_data(project)

if fracas_df is not None and not fracas_df.empty:
    # Periyodlar
    selected_periods = ['weekly', 'monthly']
    
    # PDF oluştur
    buffer = create_management_pdf(project, fracas_df, selected_periods)
    
    # Dosyaya kaydet
    output_path = f'rapor_test_{project}.pdf'
    with open(output_path, 'wb') as f:
        f.write(buffer.getvalue())
    
    file_size = os.path.getsize(output_path)
    print(f"  ✓ PDF oluşturuldu: {output_path} ({file_size} bytes)")
    
    # Test: Veriler işleniyor mu
    for period in selected_periods:
        filtered = filter_by_period(fracas_df, period)
        if filtered is not None and not filtered.empty:
            vehicle_data = get_vehicle_analysis(filtered)
            system_data = get_system_analysis(filtered)
            
            print(f"    - {period}: {len(filtered)} kayıt | {len(vehicle_data)} araç | {len(system_data)} sistem")
else:
    print(f"  ✗ {project} için veri yok")

print("\n" + "="*60)
print("TEST TAMAMLANDI")
print("="*60 + "\n")
