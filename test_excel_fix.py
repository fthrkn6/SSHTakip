#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import create_app
import pandas as pd

app = create_app()
with app.app_context():
    excel_path = r'c:\Users\ferki\Desktop\bozankaya_ssh_takip\data\belgrad\BEL25_FRACAS.xlsx'
    try:
        df = pd.read_excel(excel_path, sheet_name='FRACAS', header=0, engine='openpyxl')
        print(f'OK - Excel okudu: {len(df)} satir')
        
        # Sütunları normalize et
        df.columns = df.columns.astype(str).str.replace('\n', ' ', regex=False).str.strip()
        print(f'OK - Sütunlar normalize edildi')
        
        # FRACAS ID kolonunu bul
        fracas_col = None
        for col in df.columns:
            if 'fracas' in col.lower() and 'id' in col.lower():
                fracas_col = col
                break
        print(f'OK - FRACAS ID sütunu: {fracas_col}')
        
        # Null mask
        null_mask = df[fracas_col].isna()
        print(f'    Null satir: {null_mask.sum()}')
        
        if null_mask.any():
            first_empty_idx = null_mask.idxmax()
            print(f'    Ilk bos index: {first_empty_idx}')
            df_clean = df.loc[:first_empty_idx-1].copy()
            print(f'    Kesme sonrasi: {len(df_clean)}')
        
        df = df[df[fracas_col].notna()].copy()
        print(f'OK - Final satir sayisi: {len(df)}')
        
        if len(df) > 0:
            print(f'✓ {len(df)} kayit gösterilecek')
        else:
            print('✗ DataFrame bos!')
    except Exception as e:
        print(f'✗ Hata: {e}')
        import traceback
        traceback.print_exc()
