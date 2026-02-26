#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Equipment tablosunu SQL ile doldur
"""
import sqlite3
import pandas as pd
import os

conn = sqlite3.connect('instance/ssh_takip_bozankaya.db')
cur = conn.cursor()

print("Equipment tablosu doldurulmasi...")

# Veriler.xlsx'ten araclari oku
veriler_file = os.path.join('data', 'belgrad', 'Veriler.xlsx')
df = pd.read_excel(veriler_file, sheet_name='Sayfa2')
tram_ids = [str(int(t)) for t in df['tram_id'].dropna().unique()]

# km_data.xlsx'ten KM degerlerini oku
km_file = os.path.join('data', 'belgrad', 'km_data.xlsx')
df_km = pd.read_excel(km_file)
km_map = {}
for _, row in df_km.iterrows():
    tram_id = str(row['tram_id'])
    km_map[tram_id] = {
        'current_km': int(row['current_km']) if row['current_km'] else 0,
        'notes': str(row.get('notes', '')) or ''
    }

# Mevcut araclari sil
cur.execute("DELETE FROM equipment WHERE project_code='belgrad' AND equipment_type='Tramvay'")
conn.commit()
print(f"Mevcut araçlar silindi")

# Yeni araclari ekle
count = 0
for tram_id in sorted(tram_ids):
    km_info = km_map.get(tram_id, {})
    current_km = km_info.get('current_km', 0)
    notes = km_info.get('notes', '')
    
    cur.execute("""
        INSERT INTO equipment 
        (equipment_code, name, equipment_type, current_km, monthly_km, notes, project_code)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        tram_id,
        f'Tramvay {tram_id}',
        'Tramvay',
        current_km,
        0,
        notes,
        'belgrad'
    ))
    count += 1

conn.commit()
print(f"[OK] {count} araç eklendi")

# Dogrulama
cur.execute("SELECT COUNT(*), SUM(current_km) FROM equipment WHERE project_code='belgrad' AND equipment_type='Tramvay'")
total, total_km = cur.fetchone()
print(f"[OK] Toplam: {total} araç, {total_km or 0} km")

conn.close()
