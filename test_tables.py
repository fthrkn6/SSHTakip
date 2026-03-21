#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.reports import (
    get_fracas_data, filter_by_period, 
    get_vehicle_analysis, get_system_analysis,
    get_supplier_system_matrix, PROJECTS
)

# Test projesi
project = 'belgrad'
periods = ['monthly', 'yearly']

print(f'\n[1] {project} icin veri yükleniyor...')
fracas_df = get_fracas_data(project)

if fracas_df is None or fracas_df.empty:
    print(f'ERROR: {project} için veri bulunamadı')
    sys.exit(1)

print(f'✓ {len(fracas_df)} kayıt yüklendi')
print(f'  Sütunlar: {list(fracas_df.columns)[:10]}...')

# Her periyot için test
for period in periods:
    print(f'\n[2] Periyot Test: {period}')
    
    filtered = filter_by_period(fracas_df, period)
    
    if filtered is None or filtered.empty:
        print(f'  [!] {period} için veri yok')
        continue
    
    print(f'  ✓ {len(filtered)} kayıt bulundu')
    
    # Vehicle analiz
    vdata = get_vehicle_analysis(filtered)
    if vdata:
        print(f'  ✓ Vehicle analiz: {len(vdata)} araç')
        print(f'    İlk araç: {vdata[0]}')
    else:
        print(f'  [!] Vehicle analiz boş')
    
    # System analiz
    sdata = get_system_analysis(filtered)
    if sdata:
        print(f'  ✓ System analiz: {len(sdata)} sistem')
        print(f'    İlk sistem: {sdata[0]}')
    else:
        print(f'  [!] System analiz boş')
    
    # Matrix
    mdata = get_supplier_system_matrix(filtered)
    if mdata:
        print(f'  ✓ Tedarikçi-Sistem matrix: {len(mdata)} sistem')
        print(f'    İlk satır: {list(mdata.items())[:1]}')
    else:
        print(f'  [!] Matrix boş')

print('\n✓ Tum test tamamlandı - verileri almak sorun degil')
