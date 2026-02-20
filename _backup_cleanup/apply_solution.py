#!/usr/bin/env python3
"""ÇÖZÜM UYGULAMASI - Excel'i SOURCE OF TRUTH Yap"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment, ServiceStatus
from datetime import date
import pandas as pd

app = create_app()

with app.app_context():
    project = 'belgrad'
    today = str(date.today())
    
    print("\n" + "="*100)
    print("🔧 ÇÖZÜM UYGULAMASI")
    print("="*100)
    
    # ===== ADIM 1: ServiceStatus'ten belgrad- format araçları sil =====
    print("\n1️⃣  ServiceStatus: belgrad- FORMAT ARAÇLARI SİL")
    print("-" * 100)
    
    old_records = ServiceStatus.query.filter(
        ServiceStatus.tram_id.like('belgrad-%'),
        ServiceStatus.project_code == project
    ).all()
    
    print(f"❌ SİLİNECEK KAYITLAR: {len(old_records)} kaydı")
    for record in old_records[:3]:
        print(f"   - {record.tram_id} ({record.date})")
    if len(old_records) > 3:
        print(f"   ... ve {len(old_records)-3} daha")
    
    for record in old_records:
        db.session.delete(record)
    db.session.commit()
    
    print(f"✅ SİL: {len(old_records)} kaydı silindi")
    
    # ===== ADIM 2: Equipment table'a 1556 ekle =====
    print("\n2️⃣  Equipment: 1556 araçsı EKLE")
    print("-" * 100)
    
    existing = Equipment.query.filter_by(
        equipment_code='1556',
        project_code=project
    ).first()
    
    if not existing:
        new_equipment = Equipment(
            equipment_code='1556',
            name='Belgrad - 1556',
            project_code=project,
            parent_id=None,
            status='aktif',
            location='Belgrad' if hasattr(Equipment, 'location') else None
        )
        db.session.add(new_equipment)
        db.session.commit()
        print(f"✅ EKLENDI: 1556 araçsı Equipment table'a eklendi")
    else:
        print(f"✅ VARSA: 1556 zaten var")
    
    # ===== ADIM 3: ServiceStatus'e 1556 için bugünün kaydı ekle =====
    print("\n3️⃣  ServiceStatus: 1556 İÇİN BUGÜN KAYDINI EKLE")
    print("-" * 100)
    
    existing_status = ServiceStatus.query.filter_by(
        tram_id='1556',
        date=today,
        project_code=project
    ).first()
    
    if not existing_status:
        new_status = ServiceStatus(
            tram_id='1556',
            date=today,
            status='Servis',  # Varsayılan olarak aktif
            project_code=project,
            sistem='',
            alt_sistem='',
            aciklama=''
        )
        db.session.add(new_status)
        db.session.commit()
        print(f"✅ EKLENDI: 1556 için bugün ({today}) kaydı eklendi")
    else:
        print(f"✅ VARSA: 1556 zaten bugün kaydı var")
    
    # ===== ADIM 4: Doğrulama =====
    print("\n4️⃣  DOĞRULAMA")
    print("-" * 100)
    
    # Excel'den oku
    excel_file = 'data/belgrad/Veriler.xlsx'
    df = pd.read_excel(excel_file, sheet_name='Sayfa2', header=0)
    excel_trams = sorted([str(x) for x in df['tram_id'].unique().tolist()])
    
    # Equipment'ten oku
    equipment_list = Equipment.query.filter_by(
        project_code=project,
        parent_id=None
    ).order_by(Equipment.equipment_code).all()
    db_trams = sorted([eq.equipment_code for eq in equipment_list])
    
    # ServiceStatus'ten oku
    status_query = ServiceStatus.query.filter_by(
        project_code=project,
        date=today
    ).all()
    status_trams = sorted(list(set([ss.tram_id for ss in status_query])))
    
    print(f"\n📊 Sonuç:")
    print(f"   Excel: {len(excel_trams)} araç (1556? {('1556' in excel_trams)})")
    print(f"   Equipment: {len(db_trams)} araç (1556? {('1556' in db_trams)})")
    print(f"   ServiceStatus: {len(status_trams)} araç (1556? {('1556' in status_trams)})")
    
    # Uyuşması kontrol et
    excel_set = set(excel_trams)
    db_set = set(db_trams)
    status_set = set(status_trams)
    
    excel_db_match = (excel_set == db_set)
    excel_status_match = (excel_set == status_set)
    
    print(f"\n   Excel vs Equipment: {'✅ EŞLEŞİYOR' if excel_db_match else '❌ UYUŞMUYOR'}")
    print(f"   Excel vs ServiceStatus: {'✅ EŞLEŞİYOR' if excel_status_match else '❌ UYUŞMUYOR'}")
    
    if not excel_db_match:
        diff = excel_set - db_set or db_set - excel_set
        print(f"   Fark: {diff}")
    
    if not excel_status_match:
        diff = excel_set - status_set or status_set - excel_set
        print(f"   Fark: {diff}")
    
    print("\n" + "="*100)
    print("✅ TAMAMLANDI")
    print("="*100)
    print(f"""
Şimdi:
  ✅ Excel: {len(excel_trams)} araç
  ✅ Equipment: {len(db_trams)} araç
  ✅ ServiceStatus: {len(status_trams)} araç
  
Sonraki Adım: Tüm routes EXCEL'DEN çekmeye başlasın
""")
    print("="*100 + "\n")
