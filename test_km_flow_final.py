#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KM giriş ve okuma test
"""
import sys
sys.path.insert(0, '.')

from app import create_app
from models import Equipment, db

app = create_app()

with app.app_context():
    print("="*70)
    print("KM GIRISİ VE OKUMA TEST")
    print("="*70)
    
    # 1. Equipment listesini getir
    print("\n[1] Tramvay listesi (/tramvay-km sayfası):")
    equipments = Equipment.query.filter_by(project_code='belgrad', equipment_type='Tramvay').all()
    print(f"    Araç sayısı: {len(equipments)}")
    
    if len(equipments) > 0:
        # İlk araçla test yap
        test_eq = equipments[0]
        print(f"    Test araç: {test_eq.equipment_code}")
        
        # 2. KM değeri gir
        print(f"\n[2] KM degeri gir ({test_eq.equipment_code}):")
        old_km = test_eq.current_km or 0
        test_eq.current_km = 50000
        db.session.commit()
        print(f"    Eski: {old_km} km -> Yeni: 50000 km")
        
        # 3. Equipment tablosundan oku
        print(f"\n[3] Equipment tablosundan oku:")
        eq_check = Equipment.query.filter_by(equipment_code=test_eq.equipment_code, project_code='belgrad').first()
        print(f"    {eq_check.equipment_code}: {eq_check.current_km} km")
        
        # 4. get_tramvay_list_with_km() ile oku
        print(f"\n[4] get_tramvay_list_with_km() ile oku (bakim-planlari sayfası):")
        try:
            from utils_project_excel_store import get_tramvay_list_with_km
            result = get_tramvay_list_with_km('belgrad')
            print(f"    Araç sayısı: {len(result)}")
            
            # Test araçı bul
            for eq in result:
                if eq.equipment_code == test_eq.equipment_code:
                    print(f"    {eq.equipment_code}: {eq.current_km} km (BULUNDU)")
                    break
        except Exception as e:
            print(f"    ERROR: {e}")
        
        print("\n" + "="*70)
        print("SONUC: Girilen veriler tum sayfalarda gorulmelidir!")
        print("="*70)
    else:
        print("    ERROR: Equipment listesi bos!")
