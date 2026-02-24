#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tüm sayfaların sync durumunu kontrol et
"""

import subprocess
import re

app_file = r'c:\Users\fatiherkin\Desktop\bozankaya_ssh_takip\app.py'

# Grep commands
routes = [
    ('/tramvay-km', 'line ~2563'),
    ('/bakim-planlari', 'line ~1513'),
    ('/api/bakim-verileri', 'line ~1600')
]

print("\n" + "="*80)
print("HAFIF SİSTEM KONTROL - BOOTSTRAP/SYNC İŞLEMLERİ")
print("="*80)

# Grep sonuçları
with open(app_file, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Üç route'u kontrol et
patterns = [
    (1520, 1530, 'bootstraпp_km_excel_from_equipment'),
    (1620, 1630, 'sync_km_excel_to_equipment'),
    (2585, 2595, 'bootstrap_km_excel_from_equipment')
]

# Kontrol et
print(f"\n{'Sayfa':<25} {'Bootstrap Fonksiyonu':<30} {'Sync Fonksiyonu':<30}")
print("-"*80)

# /bakim-planlari
bakim_has_bootstrap = 'bootstrap_km_excel_from_equipment' in '\n'.join(lines[1515:1535])
bakim_has_sync = 'sync_km_excel_to_equipment' in '\n'.join(lines[1515:1535])
print(f"{'Bakım Planları':<25} {'VAR ✅' if bakim_has_bootstrap else 'YOK ❌':<30} {'VAR ✅' if bakim_has_sync else 'YOK ❌':<30}")

# /api/bakim-verileri
api_has_bootstrap = 'bootstrap_km_excel_from_equipment' in '\n'.join(lines[1620:1640])
api_has_sync = 'sync_km_excel_to_equipment' in '\n'.join(lines[1620:1640])
print(f"{'Bakım Verileri API':<25} {'VAR ✅' if api_has_bootstrap else 'YOK ❌':<30} {'VAR ✅' if api_has_sync else 'YOK ❌':<30}")

# /tramvay-km
tramvay_has_bootstrap = 'bootstrap_km_excel_from_equipment' in '\n'.join(lines[2585:2605])
tramvay_has_sync = 'sync_km_excel_to_equipment' in '\n'.join(lines[2585:2605])
print(f"{'Tramvay KM':<25} {'VAR ✅' if tramvay_has_bootstrap else 'YOK ❌':<30} {'VAR ✅' if tramvay_has_sync else 'YOK ❌':<30}")

print("\n" + "="*80)
print("SONUÇ:")
print("="*80)

if bakim_has_bootstrap and bakim_has_sync and api_has_bootstrap and api_has_sync and tramvay_has_bootstrap and tramvay_has_sync:
    print("✅ TÜM SAYFALAR SENKRON! KM güncellenince tüm sayfalar dinamik olarak güncellenecek.")
else:
    print("❌ Bazı sayfalar hala senkronize değil!")

print("\n" + "="*80 + "\n")
