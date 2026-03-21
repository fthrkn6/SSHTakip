#!/usr/bin/env python3
"""Rapor veri çekme debug"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.reports import (
    get_fracas_data, filter_by_period, get_vehicle_analysis, 
    get_system_analysis, get_supplier_system_matrix, PROJECTS, PERIODS
)
import pandas as pd

print("\n" + "="*70)
print("RAPOR VERI DEBUG - DETAYLI ANALIZ")
print("="*70 + "\n")

# Test BELGRAD
project = 'BELGRAD'
print(f"[1] {project} verilerini yükle...")
fracas_df = get_fracas_data(project)

if fracas_df is not None and not fracas_df.empty:
    print(f"    ✓ Yüklendi: {len(fracas_df)} satır")
    print(f"    Sütunlar: {list(fracas_df.columns)[:5]}...\n")
    
    # Periyod filtreleme test
    print(f"[2] filter_by_period() test - monthly (30 gün)...")
    filtered = filter_by_period(fracas_df, 'monthly')
    
    if filtered is not None and not filtered.empty:
        print(f"    ✓ Filtrelendi: {len(filtered)} satır\n")
        
        # Vehicle analizi
        print(f"[3] get_vehicle_analysis() test...")
        vehicle_data = get_vehicle_analysis(filtered)
        if vehicle_data:
            print(f"    ✓ Bulundu: {len(vehicle_data)} araç")
            for v in vehicle_data[:3]:
                print(f"       - {v['vehicle']}: KM={v['total_km']}, MTBF={v['mtbf']:.0f}")
        else:
            print(f"    ✗ Veri bulunamadı!")
            print(f"    Kontrol: Araç sütunları = {[c for c in filtered.columns if 'araç' in c.lower() or 'ara\u00e7' in c.lower()]}")
        print()
        
        # System analizi
        print(f"[4] get_system_analysis() test...")
        system_data = get_system_analysis(filtered)
        if system_data:
            print(f"    ✓ Bulundu: {len(system_data)} sistem")
            for s in system_data[:3]:
                print(f"       - {s['system']}: {s['count']} ariza, {s['downtime_hours']:.1f}h downtime")
        else:
            print(f"    ✗ Veri bulunamadı!")
            print(f"    Kontrol: Sistem sütunları = {[c for c in filtered.columns if 'sistem' in c.lower()]}")
        print()
        
        # Supplier-System matrix
        print(f"[5] get_supplier_system_matrix() test...")
        matrix_data = get_supplier_system_matrix(filtered)
        if matrix_data:
            print(f"    ✓ Bulundu: {len(matrix_data)} sistem")
            for sys, suppliers in list(matrix_data.items())[:2]:
                print(f"       - {sys}: {len(suppliers)} tedarikçi")
        else:
            print(f"    ✗ Veri bulunamadı!")
            print(f"    Kontrol: Tedarikçi sütunları = {[c for c in filtered.columns if 'tedarik' in c.lower()]}")
        
        # Sütun detaylı liste
        print(f"\n[TÜYÜ TÜYÜ SÜTUNLAR]")
        for i, col in enumerate(filtered.columns):
            print(f"   {i:2d}: {col}")
    else:
        print(f"    ✗ Filter boş döndü!")
        print(f"    Kontrol: Tarih sütunları = {[c for c in fracas_df.columns if 'tarih' in c.lower() or 'date' in c.lower()]}")
else:
    print(f"    ✗ Veri yüklenmedi!")

print("\n" + "="*70 + "\n")
