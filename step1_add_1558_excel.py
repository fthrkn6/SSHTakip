#!/usr/bin/env python3
"""Add 1558 to Excel Veriler.xlsx"""
import sys
sys.path.insert(0, '.')

from app import create_app
from utils.project_manager import ProjectManager
import pandas as pd
import os

app = create_app()

with app.app_context():
    project = 'belgrad'
    
    print("\n" + "="*100)
    print("STEP 1: Excel'e 1558 EKL")
    print("="*100 + "\n")
    
    veriler_file = ProjectManager.get_veriler_file(project)
    
    print(f"1. Excel dosyası: {veriler_file}\n")
    
    # Excel'i oku
    df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
    
    print(f"2. Okunan veriler:")
    print(f"   Satır: {len(df)}")
    print(f"   Sütunlar: {list(df.columns)}\n")
    
    # tram_id sütunu al
    current_trams = sorted([str(t) for t in df['tram_id'].dropna().unique().tolist()])
    print(f"3. Mevcut tram_ids: {len(current_trams)}")
    print(f"   [{current_trams[0]} ... {current_trams[-1]}]\n")
    
    # 1558 ekle
    if '1558' not in current_trams:
        # Yeni satır oluştur (template kullan)
        last_row = df.iloc[-1].copy()
        last_row['tram_id'] = '1558'
        
        df = pd.concat([df, pd.DataFrame([last_row])], ignore_index=True)
        
        # Dosyaya yaz
        df.to_excel(veriler_file, sheet_name='Sayfa2', index=False)
        
        print(f"4. EKLENDI: 1558 -> Excel\n")
    else:
        print(f"4. 1558 zaten var\n")
    
    # Doğrulama
    df_verify = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
    verify_trams = sorted([str(t) for t in df_verify['tram_id'].dropna().unique().tolist()])
    
    print(f"5. DOĞRULAMA:")
    print(f"   Toplam tram_ids: {len(verify_trams)}")
    print(f"   [{verify_trams[0]} ... {verify_trams[-1]}]")
    
    if '1558' in verify_trams:
        print(f"   ✓ 1558 Excel'de VAR\n")
    else:
        print(f"   ! 1558 Excel'de YOK\n")
    
    print("="*100)
    print("✓ STEP 1 TAMAMLANDI")
    print("="*100 + "\n")
