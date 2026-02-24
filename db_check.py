import sqlite3
import os

db_path = r'c:\Users\fatiherkin\Desktop\bozankaya_ssh_takip\instance\ssh_takip.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
print('\nTüm Tablolar:')
print('=' * 50)
tables = cur.fetchall()
for t in tables:
    print(f'  - {t[0]}')

# Now check equipment
cur.execute("SELECT id, equipment_code, current_km, project_code FROM equipment WHERE (id=1 OR equipment_code=1531) ORDER BY id")
print('\n\nEquipment Kayıtları (id=1 ve code=1531):')
print('=' * 50)
rows = cur.fetchall()
if rows:
    for r in rows:
        print(f'  id={r[0]}, code={r[1]}, km={r[2]}, project={r[3]}')
else:
    print('  (Kayıt bulunamadı)')

# Check belgrad project equipment
cur.execute("SELECT COUNT(*) FROM equipment WHERE project_code='belgrad'")
cnt = cur.fetchone()
print(f'\n\nBelgrad project içinde toplam {cnt[0]} equipment kayıtı var')

conn.close()
