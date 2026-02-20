#!/usr/bin/env python3
"""Simulate dashboard page load with auto-sync"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment, ServiceStatus
from datetime import date

app = create_app()

with app.app_context():
    project = 'belgrad'
    
    print("\n" + "="*100)
    print("STEP 2: Dashboard Sayfası Yükleniyor (AUTO-SYNC)")
    print("="*100 + "\n")
    
    # ÖNCESI
    print("1. SYNC ÖNCESI Equipment:")
    eq_before = Equipment.query.filter_by(parent_id=None, project_code=project).all()
    codes_before = sorted([eq.equipment_code for eq in eq_before])
    print(f"   Toplam: {len(codes_before)}")
    print(f"   [{codes_before[0]} ... {codes_before[-1]}]")
    
    if '1558' in codes_before:
        print(f"   Status: 1558 VAR\n")
    else:
        print(f"   Status: 1558 YOK\n")
    
    # Sync çalıştır (dashboard.py route başında çalışıyor)
    print("2. AUTO-SYNC ÇALIŞIYOR (dashboard route başında)...")
    from routes.dashboard import sync_excel_to_equipment
    
    result_trams = sync_excel_to_equipment(project)
    
    print(f"   ✓ Sync tamamlandı")
    print(f"   Excel'den okunan: {len(result_trams)} araç")
    print(f"   [{result_trams[0]} ... {result_trams[-1]}]\n")
    
    # SONRASI
    print("3. SYNC SONRASI Equipment:")
    eq_after = Equipment.query.filter_by(parent_id=None, project_code=project).all()
    codes_after = sorted([eq.equipment_code for eq in eq_after])
    print(f"   Toplam: {len(codes_after)}")
    print(f"   [{codes_after[0]} ... {codes_after[-1]}]")
    
    if '1558' in codes_after:
        print(f"   Status: ✓ 1558 EKLENDI\n")
    else:
        print(f"   Status: ! 1558 HALA YOK\n")
    
    # Dashboard filter sonucu
    print("4. DASHBOARD FİLTRESİ (get_tram_ids_from_veriler):")
    from routes.dashboard import get_tram_ids_from_veriler
    
    dashboard_trams = get_tram_ids_from_veriler(project)
    print(f"   Excel from: {len(dashboard_trams)} araç")
    print(f"   [{dashboard_trams[0]} ... {dashboard_trams[-1]}]")
    
    # Equipment filter sonucu
    print("\n5. DASHBOARD EKRAN OUTPUTFİ (Equipment filter):")
    
    display_list = Equipment.query.filter(
        Equipment.equipment_code.in_(dashboard_trams),
        Equipment.parent_id.is_(None),
        Equipment.project_code == project
    ).order_by(Equipment.equipment_code).all()
    
    display_codes = [eq.equipment_code for eq in display_list]
    print(f"   Gösterilecek: {len(display_codes)} araç")
    print(f"   [{display_codes[0]} ... {display_codes[-1]}]")
    
    if '1558' in display_codes:
        print(f"   ✓ Dashboard'da 1558 GÖRÜNECEK\n")
    else:
        print(f"   ! Dashboard'da 1558 GÖRÜNMEYECEK\n")
    
    # ServiceStatus için
    print("6. ServiceStatus (Bugünün kaydı):")
    today = date.today().strftime('%Y-%m-%d')
    
    ss_1558 = ServiceStatus.query.filter_by(
        tram_id='1558',
        project_code=project,
        date=today
    ).first()
    
    if ss_1558:
        print(f"   ✓ {today}'de 1558 kaydı var (Status: {ss_1558.status})\n")
    else:
        print(f"   ! {today}'de 1558 kaydı YOK (Sayfa yüklemesinde oluşturulur)\n")
    
    # ÖZETFinal doğrulama
    print("="*100)
    if '1558' in display_codes:
        print("✓ BAŞARILI - Dashboard'da 1558 görsselenler edecegeek")
        print("✓ Excel dinamik update'leri çalışıyor")
    else:
        print("! PROBLEM - 1558 hâlâ görilnmiyor")
    print("="*100 + "\n")
