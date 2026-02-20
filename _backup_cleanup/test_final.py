#!/usr/bin/env python3
"""FINAL TEST - Tüm routes aynı veriyi gösteriyor mu?"""
import sys
sys.path.insert(0, '.')

from app import create_app
from models import Equipment, ServiceStatus
from datetime import date
import pandas as pd
import os

app = create_app()

with app.app_context():
    project = 'belgrad'
    today = str(date.today())
    
    print("\n" + "="*100)
    print("🧪 FINAL TEST - TÜM ROUTES AYNI VERIYI GÖSTERIYOR MU?")
    print("="*100 + "\n")
    
    # 1. Excel'den tram_ids oku
    veriler_path = os.path.join(app.root_path, 'data', project, 'Veriler.xlsx')
    df = pd.read_excel(veriler_path, sheet_name='Sayfa2', header=0)
    excel_trams = sorted([str(t) for t in df['tram_id'].dropna().unique().tolist()])
    print(f"1️⃣  EXCEL'DEN OKUNAN ARAÇLAR ({len(excel_trams)} adet):")
    print(f"   {excel_trams}")
    
    # 2. Equipment table'dan Dashboard'ın çekeceği veriyi simüle et
    equipment_list = Equipment.query.filter(
        Equipment.equipment_code.in_(excel_trams),
        Equipment.project_code == project
    ).order_by(Equipment.equipment_code).all()
    
    dashboard_trams = sorted([eq.equipment_code for eq in equipment_list])
    print(f"\n2️⃣  DASHBOARD TARAFINDAN ÇEKILECEK ARAÇLAR ({len(dashboard_trams)} adet):")
    print(f"   {dashboard_trams}")
    
    # 3. ServiceStatus table'dan Servis Durumu'nun çekeceği veriyi simüle et
    status_records = ServiceStatus.query.filter(
        ServiceStatus.tram_id.in_(excel_trams),
        ServiceStatus.date == today,
        ServiceStatus.project_code == project
    ).order_by(ServiceStatus.tram_id).all()
    
    status_trams = sorted(list(set([ss.tram_id for ss in status_records])))
    print(f"\n3️⃣  SERVIS DURUMU TARAFINDAN ÇEKILECEK ARAÇLAR ({len(status_trams)} adet):")
    print(f"   {status_trams}")
    
    # 4. Karşılaştır
    print("\n" + "-"*100)
    print("4️⃣  KARŞILAŞTIRMA:")
    print("-"*100)
    
    match_dashboard = (excel_trams == dashboard_trams)
    match_status = (excel_trams == status_trams)
    
    print(f"✓ Excel == Dashboard?  {'✅ EVET' if match_dashboard else '❌ HAYIR'}")
    print(f"✓ Excel == Servis Durumu? {'✅ EVET' if match_status else '❌ HAYIR'}")
    
    # 5. Özel kontrol: 1556
    print(f"\n5️⃣  ÖZEL KONTROL - 1556 ARAÇSI:")
    print(f"   Excel'de?           {'✅ EVET' if '1556' in excel_trams else '❌ HAYIR'}")
    print(f"   Dashboard'da?       {'✅ EVET' if '1556' in dashboard_trams else '❌ HAYIR'}")
    print(f"   Servis Durumda?     {'✅ EVET' if '1556' in status_trams else '❌ HAYIR'}")
    
    print("\n" + "="*100)
    if match_dashboard and match_status:
        print("✅ BAŞARILI - TÜM SAYFALAR AYNI VERİYİ GÖSTERECEK")
    else:
        print("❌ SORUN VAR")
    print("="*100 + "\n")
