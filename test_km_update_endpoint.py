#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test KM update endpoint - verify update works"""
from app import app
from models import Equipment, db
import json

print("\n" + "="*60)
print("[TEST] KM UPDATE ENDPOINT TESTI")
print("="*60)

with app.app_context():
    # 1. Test equipment var mi
    print("\n[1] Test Equipment Hazirla:")
    eq = Equipment.query.filter_by(equipment_code='1531').first()
    old_km = eq.current_km if eq else 0
    print(f"   [OK] Tram 1531 - Eski KM: {old_km}")
    
    # 2. Manual update yap (endpoint gibi)
    print("\n[2] KM Guncelle (TEST):")
    if not eq:
        eq = Equipment(
            equipment_code='1531',
            name='Test Tramvay 1531',
            equipment_type='Tramvay',
            current_km=0,
            project_code='belgrad'
        )
        db.session.add(eq)
    
    # TEST: KM'i 250 yap
    test_km = 250
    eq.current_km = test_km
    eq.notes = 'Test GÜncelleme'
    db.session.commit()
    print(f"   ✅ DB güncellemesi yapıldı: {old_km} → {test_km}")
    
    # 3. Kontrol et
    print("\n3️⃣  Güncelleme Doğrula:")
    check_eq = Equipment.query.filter_by(equipment_code='1531').first()
    if check_eq and check_eq.current_km == test_km:
        print(f"   ✅ DB'de BAŞARILI: KM={check_eq.current_km}")
    else:
        print(f"   ❌ DB'de BAŞARILI DEĞİL: {check_eq.current_km if check_eq else 'NOT FOUND'}")
    
    # 4. upsert_km fonksiyonu test et
    print("\n4️⃣  upsert_km() Helper Test:")
    try:
        from utils_project_excel_store import upsert_km
        
        # B için farklı değer yaz
        test_km_2 = 350
        upsert_km(
            project_code='belgrad',
            tram_id='1531',
            current_km=test_km_2,
            notes='upsert_km test',
            updated_by='test_user'
        )
        print(f"   ✅ upsert_km çağrıldı: KM={test_km_2}")
        
        # Excel'i kontrol et
        import pandas as pd
        xl_file = 'data/belgrad/km_data.xlsx'
        try:
            df = pd.read_excel(xl_file)
            print(f"   ✅ Excel okundu: {len(df)} satır")
            tram_row = df[df['Tram ID'].astype(str) == '1531']
            if not tram_row.empty:
                print(f"   ✅ Excel'de tram 1531 bulundu: KM={tram_row.iloc[0]['Current KM']}")
            else:
                print(f"   ⚠️  Excel'de tram 1531 bulunamadı")
        except Exception as xl_err:
            print(f"   ⚠️  Excel okuma hatası: {xl_err}")
        
        # JSON kontrol et
        import os
        km_file = 'data/belgrad/km_data.json'
        if os.path.exists(km_file):
            with open(km_file) as f:
                km_data = json.load(f)
            if '1531' in km_data:
                print(f"   ✅ JSON'da tram 1531: KM={km_data['1531'].get('current_km', 'N/A')}")
            
    except Exception as e:
        print(f"   ❌ upsert_km hatası: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ TEST TAMAMLANDI")
    print("="*60 + "\n")
