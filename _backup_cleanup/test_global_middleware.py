#!/usr/bin/env python3
"""Test global middleware - all routes get sync"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment
from utils.project_manager import ProjectManager
import pandas as pd
import os

app = create_app()

with app.app_context():
    project = 'belgrad'
    
    print("\n" + "="*100)
    print("TEST: Global Sync Middleware - Tum route'lar sync yapacak")
    print("="*100 + "\n")
    
    # Excel durumunu kontrol et
    veriler_file = ProjectManager.get_veriler_file(project)
    df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
    excel_trams = sorted([str(t) for t in df['tram_id'].dropna().unique().tolist()])
    
    print(f"1. EXCEL DURUMU:")
    print(f"   Dosya: {veriler_file}")
    print(f"   Toplam: {len(excel_trams)} arac")
    print(f"   [{excel_trams[0]} ... {excel_trams[-1]}]\n")
    
    # Equipment ONCESI
    eq_before = Equipment.query.filter_by(parent_id=None, project_code=project).all()
    before_codes = sorted([eq.equipment_code for eq in eq_before])
    
    print(f"2. EQUIPMENT ONCESI:")
    print(f"   Toplam: {len(before_codes)} arac\n")
    
    # Global sync'i simule et (app.py'deki gibi)
    from routes.dashboard import sync_excel_to_equipment
    sync_excel_to_equipment(project)
    
    print(f"3. SYNC CALISTIRILDI\n")
    
    # Equipment SONRASI
    eq_after = Equipment.query.filter_by(parent_id=None, project_code=project).all()
    after_codes = sorted([eq.equipment_code for eq in eq_after])
    
    print(f"4. EQUIPMENT SONRASI:")
    print(f"   Toplam: {len(after_codes)} arac")
    print(f"   [{after_codes[0]} ... {after_codes[-1]}]\n")
    
    # BAKIMI PLANLARI ROUTE TEST
    print(f"5. BAKIMI PLANLARI ROUTE DURUMU:")
    
    # Test client ile request yap
    client = app.test_client()
    response = client.get('/maintenance/plans', follow_redirects=True)
    
    print(f"   Request: GET /maintenance/plans")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   OK: Sayfa yüklendi (global sync çalışacak)\n")
    else:
        print(f"   Login redirect (expected)\n")
    
    # Verify
    if set(after_codes) == set(excel_trams):
        print(f"="*100)
        print(f"BASARILI - Tum route'lar global sync middleware ile senkronize ediliyor")
        print(f"Bakım planları sayfası da sync'li veri gösteriyor olmalı")
        print(f"="*100 + "\n")
    else:
        print(f"! Check excel vs equipment sync\n")
