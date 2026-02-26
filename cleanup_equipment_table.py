#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Equipment tablosunu temizle - sadece doğru araçlar olsun (1531-1555)
"""
import sqlite3

conn = sqlite3.connect('instance/ssh_takip_bozankaya.db')
cur = conn.cursor()

# Doğru tramvay kodlarını tanımla (Excel'den)
valid_trams = [str(i) for i in range(1531, 1556)]

# Belgrad Tramvay Equipment'larını al
cur.execute("SELECT id, equipment_code FROM equipment WHERE project_code='belgrad' AND equipment_type='Tramvay' ORDER BY equipment_code")
equipments = cur.fetchall()

print(f"Belgrad Tramvay Equipment'ları ({len(equipments)}):")
for eq_id, eq_code in equipments:
    status = "✓ TUTULUYOR" if str(eq_code) in valid_trams else "✗ SİLİNECEK"
    print(f"  {eq_id}: {eq_code} - {status}")

# Geçersiz araçları sil
invalid_codes = [eq[1] for eq in equipments if str(eq[1]) not in valid_trams]
print(f"\nSilinecek araçlar ({len(invalid_codes)}): {invalid_codes}")

if invalid_codes:
    for code in invalid_codes:
        cur.execute("DELETE FROM equipment WHERE equipment_code=? AND project_code='belgrad'", (str(code),))
    conn.commit()
    print(f"✓ {len(invalid_codes)} araç silindi")
else:
    print("Silinecek araç yok")

# Son durumu kontrol et
cur.execute("SELECT COUNT(*), COUNT(DISTINCT equipment_code) FROM equipment WHERE project_code='belgrad' AND equipment_type='Tramvay'")
total, unique = cur.fetchone()
print(f"\nSon durum: {total} equipment, {unique} benzersiz kod")

conn.close()
