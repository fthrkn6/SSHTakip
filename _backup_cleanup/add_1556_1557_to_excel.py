#!/usr/bin/env python3
"""Add 1556 and 1557 to Excel (final fix)"""
import sys
sys.path.insert(0, '.')

from app import create_app
from utils.project_manager import ProjectManager
import pandas as pd

app = create_app()

with app.app_context():
    project = 'belgrad'
    
    print("\nEXCEL'E 1556 VE 1557 EKLENIYOR...\n")
    
    veriler_file = ProjectManager.get_veriler_file(project)
    df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
    
    oncesi = sorted([str(t) for t in df['tram_id'].dropna().unique().tolist()])
    print(f"Oncesi: {len(oncesi)} arac: {oncesi}\n")
    
    # 1556 ve 1557 ekle (1555 ile 1558 arasina)
    new_rows = []
    for tram_id in ['1556', '1557']:
        if tram_id not in [str(t) for t in df['tram_id'].dropna().tolist()]:
            # Template: 1555'i template al
            template = df[df['tram_id'] == 1555].iloc[0].copy() if 1555 in df['tram_id'].values else df.iloc[-1].copy()
            template['tram_id'] = int(tram_id)
            new_rows.append(template)
            print(f"  + {tram_id} eklenecek")
    
    if new_rows:
        df = pd.concat([df] + [pd.DataFrame([row]) for row in new_rows], ignore_index=True)
        # Tram_id'ye gore sirala
        df['tram_id_numeric'] = pd.to_numeric(df['tram_id'], errors='coerce')
        df = df.sort_values('tram_id_numeric').drop('tram_id_numeric', axis=1).reset_index(drop=True)
        
        df.to_excel(veriler_file, sheet_name='Sayfa2', index=False)
        print(f"\nKayit: Excel updated\n")
    
    # Dogrula
    df_new = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
    sonrasi = sorted([str(t) for t in df_new['tram_id'].dropna().unique().tolist()])
    
    print(f"Sonrasi: {len(sonrasi)} arac: {sonrasi}\n")
    
    # Check
    if '1556' in sonrasi and '1557' in sonrasi:
        print("OK: 1556 ve 1557 Excel'de yok2 ver\n")
    else:
        print("PROBLEM: Hala eksik\n")
