#!/usr/bin/env python3
"""DURUM ANALİZİ - Excel vs Database - Her Route Nereden Çekiyor?"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment, ServiceStatus
from datetime import date
import pandas as pd
import os

app = create_app()

with app.app_context():
    project = 'belgrad'
    today = str(date.today())
    
    print("\n" + "="*120)
    print("🔍 DURUM ANALİZİ - VERİ KAYNAĞI UYUŞMAZLIĞI")
    print("="*120)
    
    # ===== KAYNAK 1: EXCEL =====
    print("\n1️⃣  EXCEL DOSYASI (Veriler.xlsx) - SOURCE OF TRUTH OLMASI GEREKEN")
    print("-" * 120)
    
    excel_file = 'data/belgrad/Veriler.xlsx'
    df = pd.read_excel(excel_file, sheet_name='Sayfa2', header=0)
    excel_trams = sorted([str(x) for x in df['tram_id'].unique().tolist()])
    
    print(f"\n📄 Dosya: {excel_file}")
    print(f"📊 Toplam: {len(excel_trams)} araç")
    print(f"🚊 Araçlar: {excel_trams[:5]}... {excel_trams[-3:]}")
    print(f"   ✅ 1556 var mı? {('1556' in excel_trams)}")
    
    # ===== KAYNAK 2: EQUIPMENT TABLE =====
    print("\n2️⃣  EQUIPMENT TABLE (Database) - Şu An Kullanılan")
    print("-" * 120)
    
    equipment_query = Equipment.query.filter_by(
        project_code=project,
        parent_id=None
    ).all()
    db_trams = sorted([eq.equipment_code for eq in equipment_query])
    
    print(f"\n🗄️  Tablo: equipment (project_code={project}, parent_id=NULL)")
    print(f"📊 Toplam: {len(db_trams)} araç")
    print(f"🚊 Araçlar: {db_trams[:5]}... {db_trams[-3:]}")
    print(f"   ✅ 1556 var mı? {('1556' in db_trams)}")
    
    # ===== KAYNAK 3: SERVICE_STATUS TABLE =====
    print("\n3️⃣  SERVICE_STATUS TABLE (Bugün's Data)")
    print("-" * 120)
    
    status_query = ServiceStatus.query.filter_by(
        project_code=project,
        date=today
    ).all()
    status_trams = sorted(list(set([ss.tram_id for ss in status_query])))
    
    print(f"\n🗄️  Tablo: service_status (project_code={project}, date={today})")
    print(f"📊 Toplam: {len(status_trams)} araç")
    print(f"🚊 Araçlar: {status_trams[:5]}... {status_trams[-3:]}")
    print(f"   ✅ 1556 var mı? {('1556' in status_trams)}")
    
    # ===== FARK ANALİZİ =====
    print("\n" + "="*120)
    print("⚠️  UYUŞMAZLIKLAR")
    print("="*120)
    
    excel_set = set(excel_trams)
    db_set = set(db_trams)
    status_set = set(status_trams)
    
    print(f"\nExcel - Database farkı:")
    excel_only = excel_set - db_set
    db_only = db_set - excel_set
    
    if excel_only:
        print(f"  ❌ Excel'de VAR, Database'de YOK: {sorted(list(excel_only))}")
    if db_only:
        print(f"  ❌ Database'de VAR, Excel'de YOK: {sorted(list(db_only))}")
    if not excel_only and not db_only:
        print(f"  ✅ Tamamen eşleşiyor")
    
    print(f"\nExcel - ServiceStatus farkı:")
    excel_status_diff = excel_set - status_set
    status_excel_diff = status_set - excel_set
    
    if excel_status_diff:
        print(f"  ❌ Excel'de VAR, ServiceStatus'te YOK: {sorted(list(excel_status_diff))}")
    if status_excel_diff:
        print(f"  ❌ ServiceStatus'te VAR, Excel'de YOK: {sorted(list(status_excel_diff))}")
    
    # ===== ROUTES ANALİZİ =====
    print("\n" + "="*120)
    print("🗺️  ROUTES - KİMDE NE SORUNU VAR")
    print("="*120)
    
    print("""
┌─ DASHBOARD (/dashboard/)
│  └─ get_tram_ids_from_veriler() kullanıyor (Excel)
│     ├─ Excel okur: {excel_trams çekiliyor}
│     └─ Equipment.query.filter(equipment_code.in_(excel_ids))
│        = Sadece Excel'deki araçlar gösteriliyor
│        = 1556 görmüyor ❌ (Equipment table'de 1556 yok)
│
├─ /servis/durumu/ (Service Status Page)
│  └─ get_tram_ids_from_veriler() kullanıyor (Excel)
│     ├─ Excel okur: {excel_trams çekiliyor}
│     └─ ServiceStatus.query.filter(tram_id.in_(excel_ids))
│        = 1556 gösteriyor ✅ (Excel'de 1556 var)
│
└─ /bakim-planlari/ (Maintenance Planning)
   └─ ??? Hangi kaynağı kullanıyor?
      ├─ Excel mi? Database mi? Hybrid mi?
      └─ 1556 görünüyor mu?
""")
    
    print("="*120)
    print("🎯 SORUNUN KÖKÜ")
    print("="*120)
    print(f"""
Excel'de: {len(excel_trams)} araç (1556 HAKKINDA!)
Database: {len(db_trams)} araç (1556 HOSLANMIYOR!)

Ne Oldu:
1. Excel'e 1556 ekledin ✅
2. Dashboard: Equipment table'dan çekiyor → 1556 SİLİNMEDİ kaldı 1555 ❌
3. Service Status: Excel'den çekiyor → 1556 GÖRÜYOR ✅
4. Maintenance: ??? TBD

🔴 SOLUTION:
   → Equipment table'a 1556 EKLE
   → VEYA Excel'i Database'le senkronize et
   → VEYA HER YER SADECE EXCEL'DEN ÇEKSIN

SONUÇ: En kolay = Equipment table'a 1556 ekle + Excel ve Database senkron tut
""")
    
    print("="*120 + "\n")
