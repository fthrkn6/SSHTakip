#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import os

# km_data.xlsx'i oku
km_file = os.path.join('data', 'belgrad', 'km_data.xlsx')
if os.path.exists(km_file):
    try:
        df = pd.read_excel(km_file)
        print(f'KM Excel Columns: {list(df.columns)}')
        print(f'Total rows: {len(df)}')
        
        # tram_id column
        tram_col = None
        for col in df.columns:
            if col.lower() in ['tram_id', 'tram id']:
                tram_col = col
                break
        
        if tram_col:
            trams = df[tram_col].dropna().unique()
            print(f'\nTotal unique tram_ids: {len(trams)}')
            print(f'Tram IDs: {sorted([str(t) for t in trams])}')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
else:
    print('km_data.xlsx not found')
