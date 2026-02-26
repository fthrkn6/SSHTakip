#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('instance/ssh_takip_bozankaya.db')
cur = conn.cursor()

# Belgrad equipment'lerin type'ını Tramvay olarak ayarla
cur.execute("UPDATE equipment SET equipment_type='Tramvay' WHERE project_code='belgrad'")
conn.commit()

# Dogrulama
cur.execute("SELECT COUNT(*) FROM equipment WHERE project_code='belgrad' AND equipment_type='Tramvay'")
count = cur.fetchone()[0]
print(f"[OK] Belgrad Tramvay Equipment: {count}")

# Tüm projekteleri de düzelt (diğer projeler de equipment_type boş olabilir)
cur.execute("SELECT DISTINCT project_code FROM equipment WHERE equipment_type IS NULL")
projects = cur.fetchall()
for proj in projects:
    project_code = proj[0]
    cur.execute(f"UPDATE equipment SET equipment_type='Tramvay' WHERE project_code=?", (project_code,))
conn.commit()

print("[OK] Tum equipment type'lari guncellendi")

# Final check
cur.execute("SELECT COUNT(*) FROM equipment WHERE equipment_type='Tramvay'")
total = cur.fetchone()[0]
print(f"[OK] Toplam Tramvay Equipment: {total}")

conn.close()
