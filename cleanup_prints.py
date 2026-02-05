#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove debug print statements from app.py
"""

import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Debug print keywords to remove
debug_keywords = [
    'POST /yeni-ariza-bildir',
    'Gelen form alanları',
    'Form\'dan gelen FRACAS',
    'Arıza Listesi max row',
    'FRACAS ID hesaplandı',
    'FRACAS ID okuma hatası',
    'Hesaplanan FRACAS ID',
    'Arıza Listesi dosyası oluşturuldu',
    'Veri yazılacak satır',
    'Arıza kaydedildi',
    'Arıza Listesi yüklendi',
    'Arıza Listesi okuma hatası',
    'Arıza Listesi işlem',
    'Parts lookup hatası',
    'Excel okuma hatası',
    'Excel okuşta hata',
    'Sistem verileri yüklenirken',
    'EXCEL\'DEN ÇEKILEN',
    'İstatistikler',
    'ServiceStatus hatası',
    'create_app finished',
    'SSH Takip System',
    'Sample data initialized',
    'Sayfa2 yükleme hatası',
    'Veriler.xlsx okuma',
]

cleaned_lines = []
for line in lines:
    # Skip lines that contain debug prints
    if 'print(' in line and any(keyword in line for keyword in debug_keywords):
        continue
    # Also skip print lines with emoji patterns that are clearly debug
    if 'print(' in line and any(emoji in line for emoji in ['📤', '📋', '🔢', '📊', '✅', '❌', '✓', '📁', '📝']):
        continue
    cleaned_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(cleaned_lines)

print('✅ Print statements removed successfully')
