#!/usr/bin/env python3
"""Test with realistic Flask test client"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment, User
from utils.project_manager import ProjectManager
import pandas as pd
from datetime import date

app = create_app()

with app.app_context():
    project = 'belgrad'
    
    print("\n" + "="*100)
    print("TEST: Flask test client - before_request middleware")
    print("="*100 + "\n")
    
    # STEP 1: Excel'e 1561 ekle
    print("1. EXCEL'E 1561 EKLENİYOR...\n")
    
    veriler_file = ProjectManager.get_veriler_file(project)
    df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
    
    if '1561' not in [str(t) for t in df['tram_id'].dropna().tolist()]:
        last_row = df.iloc[-1].copy()
        last_row['tram_id'] = '1561'
        df = pd.concat([df, pd.DataFrame([last_row])], ignore_index=True)
        df.to_excel(veriler_file, sheet_name='Sayfa2', index=False)
        print(f"   ✓ 1561 Excel'e eklendi\n")
    
    # Equipment ÖNCESI
    print("2. EQUIPMENT ÖNCESI:")
    eq_before = Equipment.query.filter_by(parent_id=None, project_code=project).all()
    codes_before = sorted([eq.equipment_code for eq in eq_before])
    print(f"   Toplam: {len(codes_before)}")
    print(f"   [{codes_before[0]} ... {codes_before[-1]}]")
    print(f"   1561 var mı? {('1561' in codes_before)}\n")
    
    # STEP 2: Test client ile dashboard request yap
    print("3. TEST CLIENT WITH SESSION:")
    
    client = app.test_client()
    
    # Session context'te request yap
    with client:
        # GET request (before_request çalışacak)
        response = client.get('/dashboard/', follow_redirects=True)
        
        print(f"   Request: GET /dashboard/")
        print(f"   Status: {response.status_code}")
        
        # Response header'ında login redirect var mı?
        if response.status_code == 200:
            print(f"   ✓ Page loaded (requires login - maybe redirected)\n")
        elif response.status_code in [301, 302]:
            print(f"   ! Redirected (login required)\n")
        else:
            print(f"   ! Error: {response.status_code}\n")
    
    # Equipment SONRASI
    print("4. EQUIPMENT SONRASI (AUTO-SYNC):")
    eq_after = Equipment.query.filter_by(parent_id=None, project_code=project).all()
    codes_after = sorted([eq.equipment_code for eq in eq_after])
    print(f"   Toplam: {len(codes_after)}")
    print(f"   [{codes_after[0]} ... {codes_after[-1]}]")
    print(f"   1561 var mı? {('1561' in codes_after)}\n")
    
    if '1561' in codes_after and '1561' not in codes_before:
        print("="*100)
        print("✓ TEST BAŞARILI - middleware'in sync'i çalıştırdığını doğruladı")
        print("="*100 + "\n")
    else:
        print("="*100)
        print("! TEST FAILED - 1561 yine de eklenmedi")
        print("="*100 + "\n")
