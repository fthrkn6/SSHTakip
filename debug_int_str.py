#!/usr/bin/env python3
"""Debug: int/str karşılaştırma hatası - Tüm Projeler"""
import sys
import os
import traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.reports import (
    get_fracas_data, filter_by_period, get_vehicle_analysis, 
    get_system_analysis, get_supplier_system_matrix, PROJECTS
)

print("\n" + "="*70)
print("DEBUG: int/str HATA - Tüm Projeler")
print("="*70 + "\n")

all_projects = list(PROJECTS.keys())

for project in all_projects:
    print(f"[{project.upper()}]")
    try:
        fracas_df = get_fracas_data(project)
        
        if fracas_df is None or fracas_df.empty:
            print(f"  ⊘ Veri yok\n")
            continue
        
        # Tüm periyodları test et
        filtered = filter_by_period(fracas_df, 'monthly')
        if filtered is not None and not filtered.empty:
            vehicle_data = get_vehicle_analysis(filtered)
            system_data = get_system_analysis(filtered)
            matrix_data = get_supplier_system_matrix(filtered)
            print(f"  ✓ {len(vehicle_data)} araç, {len(system_data)} sistem\n")
        else:
            print(f"  ⊘ monthly filtrede veri yok\n")
    
    except Exception as e:
        print(f"  ✗ HATA: {type(e).__name__}: {str(e)[:60]}")
        print(f"  Traceback:")
        traceback.print_exc()
        print()

print("="*70 + "\n")
