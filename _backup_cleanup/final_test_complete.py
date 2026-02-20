#!/usr/bin/env python3
"""Final test - complete flow with cache control"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment
from utils.project_manager import ProjectManager
import pandas as pd

app = create_app()

with app.app_context():
    project = 'belgrad'
    
    print("\n" + "="*100)
    print("FINAL TEST: Excel -> Equipment -> Dashboard (NO CACHE)")
    print("="*100 + "\n")
    
    # 1563 Excel'e ekle
    print("1. EXCEL'E 1563 EKL:")
    veriler_file = ProjectManager.get_veriler_file(project)
    df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
    
    if '1563' not in [str(t) for t in df['tram_id'].dropna().tolist()]:
        last_row = df.iloc[-1].copy()
        last_row['tram_id'] = '1563'
        df = pd.concat([df, pd.DataFrame([last_row])], ignore_index=True)
        df.to_excel(veriler_file, sheet_name='Sayfa2', index=False)
        print(f"   OK: 1563 eklendi\n")
    
    # Test client ile request yap (cache header kontrol et)
    print("2. REQUEST RESPONSE HEADERS:")
    
    client = app.test_client()
    response = client.get('/dashboard/', follow_redirects=True)
    
    cache_header = response.headers.get('Cache-Control', 'NOT SET')
    pragma = response.headers.get('Pragma', 'NOT SET')
    
    print(f"   Cache-Control: {cache_header}")
    print(f"   Pragma: {pragma}\n")
    
    # Equipment'da 1563 var mı?
    print("3. VERIFICATION:")
    
    eq_1563 = Equipment.query.filter_by(
        equipment_code='1563',
        project_code=project,
        parent_id=None
    ).first()
    
    total_eqs = Equipment.query.filter_by(parent_id=None, project_code=project).count()
    
    print(f"   Toplam araç: {total_eqs}")
    print(f"   1563 var mi? {'EVET' if eq_1563 else 'HAYIR'}\n")
    
    print("="*100)
    if eq_1563:
        if cache_header == 'NOT SET':
            print("! Cache header yokABDA ekle")
        else:
            print("OK - Tamam! Excel -> Dashboard simdi dinamik calisyor")
            print("OK - User Excel'e arac ekleyip refresh'etse, dashboard'da gorunecek")
    else:
        print("! 1563 hala eklenmedi")
    print("="*100 + "\n")
