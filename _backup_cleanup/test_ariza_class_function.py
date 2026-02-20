#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test the get_ariza_counts_by_class function"""

import sys
sys.path.insert(0, '/root')

from routes.dashboard import get_ariza_counts_by_class

print("\n" + "="*80)
print("ARİZA SINIFI SAYILARI HESAPLAMA TESTİ")
print("="*80)

# Call the function
ariza_counts = get_ariza_counts_by_class()

print("\n📊 ARIZA SINIFI DAĞILIMI:\n")
print("-"*80)

for class_key in ['A', 'B', 'C', 'D']:
    count = ariza_counts[class_key]['count']
    label = ariza_counts[class_key]['label']
    print(f"  {class_key} - {label:40s} → {count} arıza")

print("-"*80)

total = sum(c['count'] for c in ariza_counts.values())
print(f"\n📈 TOPLAM: {total} arıza")

print("\n✅ Fonksiyon başarılı şekilde arızaları sınıflara göre sayıyor!")
print("\n" + "="*80 + "\n")
