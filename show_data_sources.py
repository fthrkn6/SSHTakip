#!/usr/bin/env python3
"""VERİ KAYNAKLARI GÖSTER - Hangi datadan geldiğini göster"""
import sys
sys.path.insert(0, '.')

from app import create_app
from models import Equipment, User
import pandas as pd
import os
import json

app = create_app()

with app.app_context():
    print("\n" + "="*100)
    print("🔍 VERİ KAYNAKLARI - HANGI DATADAN 50 ARAÇ GELDİ?")
    print("="*100 + "\n")
    
    # ===== KAYNAK 1: Equipment Table =====
    print("1️⃣  EQUIPMENT TABLE (Database)")
    print("-" * 100)
    belgrad_eq = Equipment.query.filter_by(
        project_code='belgrad',
        parent_id=None
    ).order_by(Equipment.equipment_code).all()
    
    print(f"🗄️  Toplam Equipment (parent_id=None): {len(belgrad_eq)}")
    print(f"Verileri:")
    eq_ids = []
    for i, eq in enumerate(belgrad_eq, 1):
        eq_ids.append(eq.equipment_code)
        if i <= 10 or i > len(belgrad_eq) - 5:
            print(f"   {i:2d}. {eq.equipment_code:10s} -> {eq.name}")
        elif i == 11:
            print(f"   ... ({len(belgrad_eq) - 15} more items) ...")
    
    # ===== KAYNAK 2: Excel File =====
    print("\n2️⃣  VERILER.XLSX (Excel File)")
    print("-" * 100)
    excel_file = 'data/belgrad/Veriler.xlsx'
    print(f"📄 Dosya: {excel_file}")
    print(f"📍 Path: {os.path.abspath(excel_file)}")
    print(f"✓ Exists: {os.path.exists(excel_file)}")
    
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file, sheet_name='Sayfa2', header=0)
        print(f"\n📊 Excel Veri:")
        print(f"   Satır sayısı: {len(df)}")
        print(f"   Sütunlar: {list(df.columns)}")
        print(f"   Veriler:")
        
        excel_ids = []
        for i, val in enumerate(df['tram_id'].values, 1):
            excel_ids.append(str(val))
            if i <= 10 or i > len(df) - 5:
                print(f"      {i:2d}. {str(val)}")
            elif i == 11:
                print(f"      ... ({len(df) - 15} more items) ...")
    else:
        print(f"   ❌ DOSYA BULUNAMADI!")
        excel_ids = []
    
    # ===== FALLBACK LOGIC =====
    print("\n3️⃣  FALLBACK LOGIC (routes/service_status.py)")
    print("-" * 100)
    print("""
Kod Flow:
  get_tram_ids_from_veriler(project_code='belgrad'):
    1. Excel dosyası var mı? → data/belgrad/Veriler.xlsx
    2. ✅ VARSA: Excel'den 'tram_id' sütununu oku → 25 araç
    3. ❌ YOKSA: Equipment tablosundan çek → 50 araç
    
ÖNEMLİ: routes/service_status.py satırı 213-214
    equipment_list = Equipment.query.filter(
        Equipment.equipment_code.in_(tram_ids) if tram_ids else True,  ← tram_ids=['1531','1532',...]
    """)
    
    # ===== ENDPOINT RESPONSE =====
    print("\n4️⃣  /servis/durumu/tablo ENDPOINT RESPONSE")
    print("-" * 100)
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            test_user = User.query.filter_by(email='test@test.com').first()
            if test_user:
                sess['_user_id'] = str(test_user.id)
                sess['current_project'] = 'belgrad'
        
        resp = client.get('/servis/durumu/tablo')
        data = resp.get_json()
        
        print(f"📡 HTTP: {resp.status_code} OK")
        print(f"\n{'JSON RESPONSE':^100}")
        print(json.dumps({
            'stats': data['stats'],
            'table_data_count': len(data['table_data']),
            'first_3_items': [
                {
                    'tram_id': item['tram_id'],
                    'name': item['name'],
                    'status': item['status']
                } 
                for item in data['table_data'][:3]
            ]
        }, indent=2, ensure_ascii=False))
    
    # ===== ÖNEMLI: KARŞıLAŞTIRMA =====
    print("\n5️⃣  SORUNUN KÖKÜ")
    print("-" * 100)
    
    excel_set = set(excel_ids)
    equipment_set = set(eq_ids)
    
    print(f"\nExcel'de: {len(excel_set)} araç")
    print(f"Equipment tablosunda: {len(equipment_set)} araç")
    print(f"\nFark:")
    print(f"  Excel'de VAR, Equipment'de YOK: {excel_set - equipment_set}")
    print(f"  Equipment'de VAR, Excel'de YOK: {equipment_set - excel_set}")
    
    if excel_set != equipment_set:
        print(f"\n⚠️  SORUN BULUNDU!")
        print(f"   Excel'de {len(excel_set)} araç var")
        print(f"   Equipment'de {len(equipment_set)} araç var")
        print(f"   Get_tram_ids_from_veriler() Excel okuyup: {excel_ids}")
        print(f"   Ama her 2 set de aynı ID'leri göstermiyor!")
    
    print("\n" + "="*100)
    print("ÖZETİ: Tüm açık yıl? Kaynaklar ne gösteriyor?")
    print("="*100 + "\n")
    
    if len(excel_ids) == 25 and len(eq_ids) == 50:
        print("✅ BULDUM SORUNUN KÖKÜNÜ:")
        print("   Excel: 25 araç")
        print("   Equipment: 50 araç")
        print("   Endpoint: 50 araç döndürüyor (Excel'yi okumuş ama araBurada sorun var!!")
        print("   → Excel'i güncellemen lazım VEYA Equipment'e silmen lazım")
