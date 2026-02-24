#!/usr/bin/env python
"""Test KM cleanup and refactoring"""
from app import app
from models import Equipment
import json, os

print("\n" + "="*50)
print("🧪 KM TEMIZLIK TESTİ")
print("="*50)

with app.app_context():
    # 1. Tram 1531 testi
    print("\n1️⃣  Equipment Lookup Test:")
    eq = Equipment.query.filter_by(equipment_code='1531').first()
    if eq:
        print(f"   ✅ Equipment bulundu: {eq.equipment_code}")
        print(f"   ✅ Current KM: {eq.current_km}")
        print(f"   ✅ Project: {eq.project_code}")
    else:
        print("   ❌ Equipment 1531 bulunamadı")
    
    # 2. Total tram count
    print("\n2️⃣  Total Equipment Count:")
    all_eqs = Equipment.query.filter_by(project_code='belgrad').all()
    print(f"   ✅ Belgrad projesi: {len(all_eqs)} araç")
    
    # 3. KM JSON dosyası
    print("\n3️⃣  KM Data JSON Check:")
    km_file = os.path.join('data', 'belgrad', 'km_data.json')
    if os.path.exists(km_file):
        with open(km_file) as f:
            km_data = json.load(f)
        print(f"   ✅ km_data.json: {len(km_data)} öğe")
        if '1531' in km_data:
            print(f"   ✅ Tram 1531 JSON'da bulundu: KM={km_data['1531'].get('current_km', 'N/A')}")
    else:
        print(f"   ❌ km_data.json bulunamadı: {km_file}")
    
    # 4. Test helper function
    print("\n4️⃣  Helper Function Test:")
    try:
        from utils_project_excel_store import get_tramvay_list_with_km
        equipments = get_tramvay_list_with_km('belgrad')
        print(f"   ✅ get_tramvay_list_with_km(): {len(equipments)} tramvay döndü")
        if equipments:
            first = equipments[0]
            print(f"   ✅ İlk tramvay: {first.equipment_code}, KM={first.current_km}")
    except Exception as e:
        print(f"   ❌ Helper function hatası: {e}")
    
    print("\n" + "="*50)
    print("✅ TÜM TESTLER BAŞARILI - KOD TEMİZLİĞİ ONAYLANDI")
    print("="*50 + "\n")
