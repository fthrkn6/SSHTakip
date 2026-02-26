#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('instance/ssh_takip_bozankaya.db')
cur = conn.cursor()

# Tüm equipment'ları listele
print("Tum Equipment:")
cur.execute("SELECT id, equipment_code, equipment_type, project_code FROM equipment ORDER BY project_code, equipment_code")
rows = cur.fetchall()
for row in rows:
    print(f"  {row}")

# Belgrad Tramvay count
print("\nBelgrad Tramvay equipment:")
cur.execute("SELECT COUNT(*) FROM equipment WHERE project_code='belgrad' AND equipment_type='Tramvay'")
print(f"  Count: {cur.fetchone()[0]}")

conn.close()
