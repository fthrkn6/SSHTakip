#!/usr/bin/env python3
"""Test: Multi-project PDF oluştur"""
import sys
import os
import traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.reports import (
    get_fracas_data, create_management_pdf_multi, PROJECTS, PERIODS
)

print("\n" + "="*70)
print("TEST: Multi-Project PDF")
print("="*70 + "\n")

all_projects = list(PROJECTS.keys())
print(f"[1] {len(all_projects)} proje için veri yükleniyor...")

loaded_data = {}
for proj in all_projects:
    df = get_fracas_data(proj)
    if df is not None and not df.empty:
        loaded_data[proj] = df
        print(f"  ✓ {proj.upper():10s} - {len(df)} kayıt yüklendi")
    else:
        print(f"  ⊘ {proj.upper():10s} - Veri yok")

print(f"\n[2] Multi-project PDF oluşturuluyor ({len(loaded_data)} proje)...")

try:
    selected_periods = ['monthly']
    buffer = create_management_pdf_multi(all_projects, selected_periods, loaded_data)
    
    file_size = len(buffer.getvalue())
    print(f"  ✓ PDF başarıyla oluşturuldu: {file_size:,d} bytes")
    
    # Dosyaya kaydet
    output_path = 'rapor_multi_test.pdf'
    with open(output_path, 'wb') as f:
        f.write(buffer.getvalue())
    
    print(f"  ✓ Kaydedildi: {output_path}")
    
except Exception as e:
    print(f"  ✗ HATA: {type(e).__name__}")
    print(f"  Mesaj: {str(e)}\n")
    
    print("Traceback:")
    print("="*70)
    traceback.print_exc()
    print("="*70)

print("\n" + "="*70 + "\n")
