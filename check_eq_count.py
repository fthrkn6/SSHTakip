#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('instance/ssh_takip_bozankaya.db')
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM equipment WHERE project_code='belgrad' AND equipment_type='Tramvay'")
count = cur.fetchone()[0]
print(f'Equipment sayısı: {count}')
conn.close()
