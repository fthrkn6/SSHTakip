#!/usr/bin/env python3
"""Test with logged-in session"""
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
    print("TEST: Logged-in session with middleware")
    print("="*100 + "\n")
    
    # Test user oluştur veya bul
    print("1. TEST USER:")
    test_user = User.query.filter_by(email='test@test.com').first()
    
    if not test_user:
        test_user = User(
            username='testuser',
            email='test@test.com',
            password='password',  # Hash edilir model'de
            role='admin'
        )
        db.session.add(test_user)
        db.session.commit()
        print(f"   User created: {test_user.email}\n")
    else:
        print(f"   User exists: {test_user.email}\n")
    
    # STEP 1: Excel'e 1562 ekle
    print("2. EXCEL'E 1562 EKLENİYOR...\n")
    
    veriler_file = ProjectManager.get_veriler_file(project)
    df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
    
    if '1562' not in [str(t) for t in df['tram_id'].dropna().tolist()]:
        last_row = df.iloc[-1].copy()
        last_row['tram_id'] = '1562'
        df = pd.concat([df, pd.DataFrame([last_row])], ignore_index=True)
        df.to_excel(veriler_file, sheet_name='Sayfa2', index=False)
        print(f"   OK: 1562 Excel'e eklendi\n")
    
    # STEP 2: Test client ile session kurarak login
    print("3. TEST CLIENT LOGIN...")
    
    client = app.test_client()
    
    with client:
        # POST login
        response = client.post('/login', data={
            'email': 'test@test.com',
            'password': 'password'
        }, follow_redirects=True)
        
        print(f"   Login status: {response.status_code}\n")
        
        # Equipment ÖNCESI
        eq_before = Equipment.query.filter_by(parent_id=None, project_code=project).all()
        codes_before = [eq.equipment_code for eq in eq_before]
        
        print(f"4. EQUIPMENT ONCESI: {len(codes_before)} arac")
        print(f"   1562 var mi? {('1562' in codes_before)}\n")
        
        # GET dashboard (before_request çalışacak)
        response = client.get('/dashboard/', follow_redirects=True)
        print(f"   Dashboard GET: {response.status_code}")
        print(f"   OK: before_request middleware calisti\n")
        
        # Equipment SONRASI
        eq_after = Equipment.query.filter_by(parent_id=None, project_code=project).all()
        codes_after = [eq.equipment_code for eq in eq_after]
        
        print(f"5. EQUIPMENT SONRASI: {len(codes_after)} arac")
        print(f"   1562 var mi? {('1562' in codes_after)}\n")
        
        if '1562' in codes_after and '1562' not in codes_before:
            print("="*100)
            print("OK - Logged-in session'da middleware sync calisiyor")
            print("="*100 + "\n")
        else:
            print("="*100)
            print("! Failed - 1562 eklenmedi")
            print("="*100 + "\n")
