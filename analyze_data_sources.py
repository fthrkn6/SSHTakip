#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sayfa Veri Kaynakları Analizi
"""

import subprocess
import re

# app.py dosyasından bilgi çek
app_file = r'c:\Users\fatiherkin\Desktop\bozankaya_ssh_takip\app.py'

analysis = {
    '/tramvay-km': {
        'route': 2563,
        'template_file': 'templates/tramvay_km.html',
        'veri_kaynagi': [
            'Excel: Veriler.xlsx (Sayfa2) -> tram_id',
            'Database: Equipment table'
        ],
        'bootstrap': 'bootstrap_km_excel_from_equipment() ✅',
        'sync': 'sync_km_excel_to_equipment() ✅',
        'guncel': 'EVET ✅'
    },
    '/bakim-planlari': {
        'route': 1513,
        'template_file': 'templates/bakim_planlari.html',
        'veri_kaynagi': [
            'JSON: data/belgrad/maintenance.json (hardcoded)'
        ],
        'bootstrap': 'YOK ❌',
        'sync': 'YOK ❌',
        'guncel': 'HAYIR ❌ - KM güncellenmiyor'
    },
    '/api/bakim-verileri': {
        'route': 1600,
        'template_file': 'JSON API',
        'veri_kaynagi': [
            'JSON: maintenance.json',
            'Database: Equipment table',
            'Excel: km_data.xlsx (proje bazlı)'
        ],
        'bootstrap': 'bootstrap_km_excel_from_equipment() ✅',
        'sync': 'sync_km_excel_to_equipment() ✅',
        'guncel': 'EVET ✅'
    }
}

print("\n" + "="*90)
print("SAYFA VERİ KAYNAKLARI ANALİZİ")
print("="*90)
print(f"\n{'Sayfa':<25} {'Veri Kaynağı':<30} {'Bootstrap':<15} {'Sync':<15} {'Güncel?':<10}")
print("-"*90)

for page, info in analysis.items():
    veri = ', '.join(info['veri_kaynagi'][:1])  # İlk kaynak
    bootstrap = 'VAR ✅' if '✅' in info['bootstrap'] else 'YOK ❌'
    sync = 'VAR ✅' if '✅' in info['sync'] else 'YOK ❌'
    guncel = info['guncel']
    
    print(f"{page:<25} {veri:<30} {bootstrap:<15} {sync:<15} {guncel:<10}")

print("\n" + "="*90)
print("SORUN:")
print("="*90)
print("""
❌ /bakim-planlari sayfası KM güncellenmiyor çünkü:

1. Route'da bootstrap ve sync YAPILMIYOR
   - /tramvay-km ve /api/bakim-verileri yapıyor ama /bakim-planlari yapmıyor

2. Sadece hardcoded 'data/belgrad/maintenance.json' yüklüyor
   - Dinamik proje bazlı değil

3. KM verileri elle yazmadıkça maintenance.json güncellenmez
   - /api/bakim-verileri'nin tersine

FİX:
/bakim-planlari route'unda da bootstrap ve sync eklenmelidir.
""")

print("="*90 + "\n")
