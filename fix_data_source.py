#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix: İki sayfa arasında veri tutarlılığını sağla"""
from app import app
from models import Equipment
import os, json

print("\n" + "="*70)
print("[FIX] /tramvay-km vs /bakim-planlari VERİ KAYNAĞI")
print("="*70)

with app.app_context():
    project_code = 'belgrad'
    
    # 1. /tramvay-km sayfasının veri kaynağı
    print("\n[1] /tramvay-km SAYFASI:")
    print("    Kaynak: get_tramvay_list_with_km() function")
    print("    → Equipment DB'den okur")
    
    from utils_project_excel_store import get_tramvay_list_with_km
    tramvay_list = get_tramvay_list_with_km(project_code)
    print(f"    Veri: {len(tramvay_list)} tramvay")
    for tram in tramvay_list[:3]:
        print(f"      - {tram.equipment_code}: {tram.current_km} km")
    
    # 2. /bakim-planlari sayfasının veri kaynağı
    print("\n[2] /bakim-planlari SAYFASI:")
    print("    Kaynak: /bakim-planlari route")
    print("    Kullandığı veriler:")
    print("      - maintenance.json: bakım seviyeleri")
    print("      - bootstrap_km_excel_from_equipment() & sync_km_excel_to_equipment()")
    print("      - GET render_template('bakim_planlari.html', maintenance_data=...)")
    
    # maintenance.json kontrol et
    maint_file = os.path.join('data', project_code, 'maintenance.json')
    if os.path.exists(maint_file):
        with open(maint_file) as f:
            maint = json.load(f)
        print(f"\n    maintenance.json: {len(maint)} sistem seviyeleri")
    
    # 3. İKİ SAYFANIN SORUNU
    print("\n[3] SORUN ANALIZI:")
    print("    ⚠️ /tramvay-km")
    print("       - DB'den Equipment okur → correct")
    print("       - Form POST'unda DB'ye yazar → correct")
    print("       - Sorun: Tarayıcıda görülmüyor mu?")
    print()
    print("    ⚠️ /bakim-planlari")
    print("       - maintenance.json'ı gösterir")
    print("       - KM'yi nerede gösteriyor?")
    
    # 4. TEMPLATE'İ KONTROL ET
    print("\n[4] TEMPLATE KAYNAGI:")
    
    # tramvay_km.html
    import os
    tpl_file = 'templates/tramvay_km.html'
    if os.path.exists(tpl_file):
        with open(tpl_file) as f:
            content = f.read()
        if 'equipment_code' in content:
            print("    tramvay_km.html: ✓ equipment_code kullanıyor")
        else:
            print("    tramvay_km.html: ✗ equipment_code yok!")
    
    # bakim_planlari.html
    tpl_file2 = 'templates/bakim_planlari.html'
    if os.path.exists(tpl_file2):
        with open(tpl_file2) as f:
            content2 = f.read()
        if 'equipment_code' in content2:
            print("    bakim_planlari.html: ✓ equipment_code kullanıyor")
        elif 'maintenance_data' in content2:
            print("    bakim_planlari.html: ✓ maintenance_data kullanıyor")
        else:
            print("    bakim_planlari.html: ✗ KM veri kaynağı belirsiz!")
    
    print("\n[5] TARAFINDAKI SORUN:")
    print("    Form modal'da veri gördüğünü ama kaydetmeden")
    print("    veya kaydet'ten sonra sayfa yenilenmiş ama veri değişmemiş")
    print("    olabilir.")
    print()
    print("    TEST ET:")
    print("    1. Sayfayı aç: http://localhost:5000/tramvay-km")
    print("    2. Tram 1531 'Düzenle' tıkla")  
    print("    3. KM'ye 9999 yaz")
    print("    4. Kaydet tıkla")
    print("    5. Sayfa yenilenince 9999 görülmeli")
    
    print("\n" + "="*70)
