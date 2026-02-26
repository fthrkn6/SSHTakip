#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KM veri akışını basit şekilde test et
"""
import sqlite3
import pandas as pd
import os

print("="*70)
print("KM VERİ AKIŞI KONTROLÜ")
print("="*70)

# 1. Veriler.xlsx kontrol
print("\n[1] Veriler.xlsx (Sayfa2) kontrolü:")
veriler_file = os.path.join('data', 'belgrad', 'Veriler.xlsx')
df = pd.read_excel(veriler_file, sheet_name='Sayfa2')
tram_ids = sorted([str(t) for t in df['tram_id'].dropna().unique()])
print(f"    Araçlar: {len(tram_ids)}")
print(f"    Codes: {tram_ids}")

# 2. km_data.xlsx kontrol
print("\n[2] km_data.xlsx kontrolü:")
km_file = os.path.join('data', 'belgrad', 'km_data.xlsx')
df_km = pd.read_excel(km_file)
km_ids = sorted([str(t) for t in df_km['tram_id'].dropna().unique()])
print(f"    Araçlar: {len(km_ids)}")
print(f"    Codes: {km_ids}")

# 3. Database Equipment kontrol
print("\n[3] Equipment tablosu kontrolü:")
conn = sqlite3.connect('instance/ssh_takip_bozankaya.db')
cur = conn.cursor()
cur.execute("SELECT COUNT(*), COUNT(DISTINCT equipment_code) FROM equipment WHERE project_code='belgrad' AND equipment_type='Tramvay'")
total, unique = cur.fetchone()
print(f"    Toplam Equipment: {total}, Benzersiz kod: {unique}")

cur.execute("SELECT equipment_code, current_km FROM equipment WHERE project_code='belgrad' AND equipment_type='Tramvay' ORDER BY equipment_code")
rows = cur.fetchall()
if rows:
    print(f"    Equipment detail:")
    for code, km in rows:
        km_str = f"{km} km" if km else "0 km"
        print(f"      {code}: {km_str}")
else:
    print("    (Boş - ilk senkronizasyon yapılmadı)")

# 4. Öneriler
print("\n[4] SISTEM KONTROLÜ:")
print(f"    ✓ Excel araçları (Veriler.xlsx): {len(tram_ids)} araç")
print(f"    ✓ KM dosyası (km_data.xlsx): {len(km_ids)} araç")
print(f"    {'✓' if len(km_ids) == len(tram_ids) else '⚠'} KM dosyası Excel ile eşleşiyor: {len(km_ids) == len(tram_ids)}")
print(f"    {'✓' if total == 0 else '⚠'} Equipment tablosu boş (ilk senkronizasyon için hazır): {total == 0}")

if total == 0:
    print("\n    ➜ SONRAKI ADIM: /tramvay-km sayfasını aç ve KM değerleri gir")
    print("    ➜ Girilen veriler Equipment tablosunda depolanacak")
    print("    ➜ Tüm sayfalar (bakım planları, dashboard, vb.) bu verileri görecek")

conn.close()
print("\n" + "="*70)
