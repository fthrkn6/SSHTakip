#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()
client = app.test_client()

# Giriş
response = client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)

# Session'da project var mı kontrol et
with client:
    response = client.get('/ariza-listesi')
    
    # Context'i test edelim
    print("=== SESSION VE DOSYA KONTROLÜ ===\n")
    
    # Dosya varlığını kontrol et
    excel_path = r'c:\Users\ferki\Desktop\bozankaya_ssh_takip\data\belgrad\BEL25_FRACAS.xlsx'
    print(f"Excel dosyası: {excel_path}")
    print(f"  → Var mı? {os.path.exists(excel_path)}")
    
    # Klasör içindeki dosyaları listele
    folder = r'c:\Users\ferki\Desktop\bozankaya_ssh_takip\data\belgrad'
    print(f"\nFolder {folder}:")
    if os.path.exists(folder):
        files = os.listdir(folder)
        for f in files:
            if f.endswith(('.xlsx', '.xls')):
                print(f"  ✓ {f}")
    else:
        print(f"  ✗ Klasör YOK!")
    
    # Doğrudan Excel oku
    print("\n=== DOĞRUDAN EXCEL OKUMA ===")
    import pandas as pd
    try:
        df = pd.read_excel(excel_path, sheet_name='FRACAS', header=0, engine='openpyxl')
        print(f"✓ Excel okudu: {len(df)} satır")
        
        # Temizle
        fracas_col = None
        for col in df.columns:
            if 'fracas' in col.lower() and 'id' in col.lower():
                fracas_col = col
                break
        
        if fracas_col:
            print(f"✓ FRACAS ID sütunu: {fracas_col}")
            
            # Null mask
            null_mask = df[fracas_col].isna()
            if null_mask.any():
                first_empty_idx = null_mask.idxmax()
                df_clean = df.loc[:first_empty_idx-1].copy()
                print(f"  → Kesme sonrası: {len(df_clean)} satır")
            
            df_final = df[df[fracas_col].notna()].copy()
            print(f"  → Final: {len(df_final)} satır")
        else:
            print("✗ FRACAS ID sütunu bulunamadı")
            
    except Exception as e:
        print(f"✗ Hata: {e}")
        import traceback
        traceback.print_exc()
