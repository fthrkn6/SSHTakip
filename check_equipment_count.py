#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('instance/ssh_takip_bozankaya.db')
cur = conn.cursor()

# Count
cur.execute("SELECT COUNT(*) FROM equipment WHERE project_code='belgrad' AND equipment_type='Tramvay'")
count = cur.fetchone()[0]
print(f'Total Tramvay count: {count}')

# Get codes
cur.execute("SELECT equipment_code FROM equipment WHERE project_code='belgrad' AND equipment_type='Tramvay' ORDER BY equipment_code")
codes = [row[0] for row in cur.fetchall()]
print(f'Codes: {codes}')

# Excel codes
excel_codes = [str(i) for i in range(1531, 1556)]
extra_codes = [c for c in codes if c not in excel_codes]
print(f'\nExtra codes (not in Excel): {extra_codes}')

conn.close()
