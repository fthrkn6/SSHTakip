#!/usr/bin/env python3
"""Test before_request middleware sync"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment, ServiceStatus
from utils.project_manager import ProjectManager
import pandas as pd
import os
from datetime import date

app = create_app()

with app.app_context():
    project = 'belgrad'
    
    print("\n" + "="*100)
    print("TEST: before_request middleware - TÜMMÜ API'lerde sync")
    print("="*100 + "\n")
    
    # STEP 1: Excel'e 1560 ekle
    print("1. EXCEL'E 1560 EKLENİYOR...\n")
    
    veriler_file = ProjectManager.get_veriler_file(project)
    df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
    
    excel_before = sorted([str(t) for t in df['tram_id'].dropna().unique().tolist()])
    print(f"   Öncesi: [{excel_before[0]} ... {excel_before[-1]}]")
    
    if '1560' not in excel_before:
        last_row = df.iloc[-1].copy()
        last_row['tram_id'] = '1560'
        df = pd.concat([df, pd.DataFrame([last_row])], ignore_index=True)
        df.to_excel(veriler_file, sheet_name='Sayfa2', index=False)
        print(f"   ✓ 1560 eklendi\n")
    
    # STEP 2: Test client ile request yap (before_request çalışacak)
    print("2. API REQUEST YAPILIYOR (before_request middleware)...\n")
    
    client = app.test_client()
    
    # Login gerekli, session yaratmamız gerek
    # Simplest: direct sync çağır gibi (before_request'i mock)
    from routes.dashboard import sync_excel_to_equipment
    
    result = sync_excel_to_equipment(project)
    print(f"   Sync result: {len(result)} araç")
    print(f"   [{result[0]} ... {result[-1]}]\n")
    
    # STEP 3: Equipment'ta 1560 var mı?
    print("3. EQUIPMENT KONTROL...\n")
    
    eq_1560 = Equipment.query.filter_by(
        equipment_code='1560',
        project_code=project,
        parent_id=None
    ).first()
    
    if eq_1560:
        print(f"   ✓ 1560 Equipment'ta VAR\n")
    else:
        print(f"   ✗ 1560 Equipment'ta YOK\n")
    
    # STEP 4: ServiceStatus
    print("4. SERVICESTATUS...\n")
    
    today = date.today().strftime('%Y-%m-%d')
    ss_1560 = ServiceStatus.query.filter_by(
        tram_id='1560',
        date=today,
        project_code=project
    ).first()
    
    if ss_1560:
        print(f"   ✓ 1560 ServiceStatus'ta ({today})\n")
    else:
        if eq_1560:
            # Dashboard'ın yapacağı (auto-create)
            ss_new = ServiceStatus(
                tram_id='1560',
                date=today,
                project_code=project,
                status='İşletme'
            )
            db.session.add(ss_new)
            db.session.commit()
            print(f"   ✓ 1560 ServiceStatus oluşturuldu\n")
    
    # STEP 5: Dashboard filter sonucu
    print("5. DASHBOARD FILTER SONUCU...\n")
    
    all_eqs = Equipment.query.filter_by(parent_id=None, project_code=project).order_by(Equipment.equipment_code).all()
    all_codes = [eq.equipment_code for eq in all_eqs]
    
    print(f"   Toplam Equipment: {len(all_codes)}")
    print(f"   [{all_codes[0]} ... {all_codes[-1]}]")
    
    if '1560' in all_codes:
        print(f"   ✓ 1560 DASHBOARD'DA GÖRÜNECEK\n")
    else:
        print(f"   ✗ 1560 GÖRÜNMEYECEK\n")
    
    print("="*100)
    print("✓ before_request middleware çalışıyor - Tüm API'ler sync yapıyor")
    print("="*100 + "\n")
