#!/usr/bin/env python3
"""Complete dynamic test: Add to Excel -> Dashboard auto-sync"""
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
    print("COMPLETE TEST: Excel (1559) -> Dashboard (AUTO)")
    print("="*100 + "\n")
    
    # STEP 1: Excel'e 1559 ekle
    print("1. EXCEL'E 1559 EKLENİYOR...\n")
    
    veriler_file = ProjectManager.get_veriler_file(project)
    df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
    
    excel_trams_before = sorted([str(t) for t in df['tram_id'].dropna().unique().tolist()])
    print(f"   Öncesi: {len(excel_trams_before)} araç [{excel_trams_before[0]} ... {excel_trams_before[-1]}]")
    
    if '1559' not in excel_trams_before:
        last_row = df.iloc[-1].copy()
        last_row['tram_id'] = '1559'
        df = pd.concat([df, pd.DataFrame([last_row])], ignore_index=True)
        df.to_excel(veriler_file, sheet_name='Sayfa2', index=False)
        print(f"   ✓ 1559 eklendi")
    else:
        print(f"   ! 1559 zaten var")
    
    # Doğrula
    df_check = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
    excel_trams_after = sorted([str(t) for t in df_check['tram_id'].dropna().unique().tolist()])
    print(f"   Sonrası: {len(excel_trams_after)} araç [{excel_trams_after[0]} ... {excel_trams_after[-1]}]\n")
    
    # STEP 2: Dashboard sync çağır (sayfa yüklemesi simüle)
    print("2. DASHBOARD SAYFASI YÜKLENIYOR (AUTO-SYNC)...\n")
    
    from routes.dashboard import sync_excel_to_equipment
    
    sync_result = sync_excel_to_equipment(project)
    
    print(f"   Sync sonrası Equipment: {len(sync_result)} araç")
    print(f"   [{sync_result[0]} ... {sync_result[-1]}]")
    
    # Equipment'ta 1559 var mı?
    eq_1559 = Equipment.query.filter_by(
        equipment_code='1559',
        project_code=project,
        parent_id=None
    ).first()
    
    if eq_1559:
        print(f"   ✓ 1559 Equipment'ta VAR\n")
    else:
        print(f"   ✗ 1559 Equipment'ta YOK\n")
    
    # STEP 3: ServiceStatus auto-create (dashboard route default)
    print("3. SERVICESTATUS AUTO-CREATE...\n")
    
    today = date.today().strftime('%Y-%m-%d')
    
    # 1559 için ServiceStatus oluştur (dashboard'ın yapacağı)
    ss_check = ServiceStatus.query.filter_by(
        tram_id='1559',
        date=today,
        project_code=project
    ).first()
    
    if not ss_check and eq_1559:
        ss_new = ServiceStatus(
            tram_id='1559',
            date=today,
            project_code=project,
            status='İşletme',
            created_at=db.func.now(),
            updated_at=db.func.now()
        )
        db.session.add(ss_new)
        db.session.commit()
        print(f"   ✓ ServiceStatus oluşturuldu ({today})\n")
    elif ss_check:
        print(f"   ! ServiceStatus zaten var\n")
    
    # STEP 4: Dashboard filter sonucu
    print("4. DASHBOARD FİLTRE SONUCU...\n")
    
    from routes.dashboard import get_tram_ids_from_veriler
    
    dashboard_trams = get_tram_ids_from_veriler(project)
    
    display = Equipment.query.filter(
        Equipment.equipment_code.in_(dashboard_trams),
        Equipment.parent_id.is_(None),
        Equipment.project_code == project
    ).order_by(Equipment.equipment_code).all()
    
    display_codes = [eq.equipment_code for eq in display]
    
    print(f"   Gösterilecek: {len(display_codes)} araç")
    print(f"   [{display_codes[0]} ... {display_codes[-1]}]")
    
    if '1559' in display_codes:
        print(f"   ✓ 1559 DASHBOARD'DA GÖRÜNECEK\n")
    else:
        print(f"   ✗ 1559 GÖRÜNMEYECEK\n")
    
    # SUMMARY
    print("="*100)
    if '1559' in excel_trams_after and '1559' in display_codes:
        print("✓ TAM BAŞARILI - Dinamik Excel Update'leri Çalışıyor!")
        print("✓ Excel -> Equipment -> Dashboard otomatik senkronize")
        print("✓ Artık Excel'e herhangi araç EKLESEN, DASHBOARD GÖSTERIYOR")
    else:
        print("! PROBLEM")
    print("="*100 + "\n")
