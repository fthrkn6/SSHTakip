#!/usr/bin/env python3
"""Test: Tüm kombinasyonlar"""
import sys
import os
import traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.reports import (
    get_fracas_data, filter_by_period, get_vehicle_analysis, 
    PERIODS, PROJECTS
)

print("\n" + "="*70)
print("TEST: Tüm Proje x Periyot Kombinasyonları")
print("="*70 + "\n")

all_projects = list(PROJECTS.keys())

error_count = 0
for project in all_projects:
    fracas_df = get_fracas_data(project)
    
    if fracas_df is None or fracas_df.empty:
        continue
    
    for period in PERIODS.keys():
        try:
            filtered = filter_by_period(fracas_df, period)
            if filtered is not None and not filtered.empty:
                vehicle_data = get_vehicle_analysis(filtered)
                print(f"[OK] {project:10s} + {period:8s} = {len(vehicle_data)} arac")
            else:
                print(f"[-] {project:10s} + {period:8s} = no data")
        except Exception as e:
            error_count += 1
            print(f"[ER] {project:10s} + {period:8s} = ERROR: {type(e).__name__}")
            print(f"     {str(e)[:60]}")
            print()

print("\n" + "="*70)
if error_count == 0:
    print("✓ Hiç hata yok")
else:
    print(f"✗ {error_count} hata bulundu")
print("="*70 + "\n")
