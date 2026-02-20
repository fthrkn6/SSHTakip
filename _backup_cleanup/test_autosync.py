#!/usr/bin/env python3
"""Test auto-sync functionality"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment
from datetime import date

app = create_app()

with app.app_context():
    project = 'belgrad'
    
    print("\n" + "="*100)
    print("TEST: Auto-Sync Excel -> Equipment (1558 dinamic)")
    print("="*100 + "\n")
    
    # Excel'e 1558 eklenmiş olduğunu assume et
    # (Manual: kullanıcı yapacak)
    
    print("1. EXCEL'E 1558 EKLENDİ (MANUEL)")
    print("   Action: Exceli aç, Sayfa2'ye 1558 yaz\n")
    
    # Equipment'tan önceki durumu kontrol et
    print("2. SYNC ÖNCESI Equipment tablosu:")
    
    eq_before = Equipment.query.filter_by(parent_id=None, project_code=project).all()
    eq_codes_before = sorted([eq.equipment_code for eq in eq_before])
    
    print(f"   Toplam: {len(eq_codes_before)}")
    print(f"   [{eq_codes_before[0]} ... {eq_codes_before[-1]}]")
    
    if '1558' in eq_codes_before:
        print(f"   ! 1558 zaten var")
    else:
        print(f"   ! 1558 YOK")
    
    # Auto-sync çalıştır (dashboard route'unda çalışacak böyle)
    print("\n3. AUTO-SYNC ÇALIŞIYOR...")
    from routes.dashboard import sync_excel_to_equipment
    
    tram_ids = sync_excel_to_equipment(project)
    
    print(f"   ✓ Excel'den okunan tram_ids: {len(tram_ids)}")
    print(f"   [{tram_ids[0]} ... {tram_ids[-1]}]")
    
    # Equipment sonrası durumu kontrol et
    print("\n4. SYNC SONRASI Equipment tablosu:")
    
    eq_after = Equipment.query.filter_by(parent_id=None, project_code=project).all()
    eq_codes_after = sorted([eq.equipment_code for eq in eq_after])
    
    print(f"   Toplam: {len(eq_codes_after)}")
    print(f"   [{eq_codes_after[0]} ... {eq_codes_after[-1]}]")
    
    if '1558' in eq_codes_after:
        print(f"   ✓ 1558 BAŞARIYLA EKLENDİ")
    else:
        print(f"   ! 1558 HALA YOK (Excel'de yok mu?)")
    
    # Doğrulama
    print("\n5. DOĞRULAMA:")
    
    excel_set = set(tram_ids)
    db_set = set(eq_codes_after)
    
    if excel_set == db_set:
        print(f"   ✓ Excel ve Equipment SENKRONIZE")
        print(f"   ✓ Dinamik Excel update'leri ÇALIŞACaK")
    else:
        missing = excel_set - db_set
        extra = db_set - excel_set
        print(f"   ! Fark var:")
        if missing:
            print(f"     Excel'de var, DB'de yok: {missing}")
        if extra:
            print(f"     DB'de var, Excel'de yok: {extra}")
    
    print("\n" + "="*100)
    print("✓ TEST TAMAMLANDI - Dashboard sayfasını açıp yenile")
    print("="*100 + "\n")
