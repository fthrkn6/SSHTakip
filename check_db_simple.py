import sqlite3
import os

os.chdir(r'c:\Users\fatiherkin\Desktop\bozankaya_ssh_takip')
conn = sqlite3.connect('instance/ssh_takip.db')
cur = conn.cursor()

# Check id=1 and code=1531
cur.execute("SELECT id, equipment_code, current_km FROM equipment WHERE project_code='belgrad' AND (id=1 OR equipment_code=1531) ORDER BY id")

print('\n════════════════════════════════════════')
print('VERİTABANI - Equipment Kayıtları')
print('════════════════════════════════════════')
print(f'{"ID":>5} | {"CODE":>7} | {"KM":>8}')
print('─' * 30)

rows = cur.fetchall()
if not rows:
    print("Kayıt bulunamadı!")
else:
    for row in rows:
        print(f'{row[0]:>5} | {row[1]:>7} | {row[2]:>8}')

conn.close()

print('\n════════════════════════════════════════')
if rows:
    if rows[0][2] == 100:
        print("❌ SORUN: Equipment id=1 updated (100 km)")
        print("   Yanlış tramdaki veri güncellendi!")
    else:
        print("✅ Normal: id=1 güncellemedi")
    
    if len(rows) > 1 and rows[1][2] == 100:
        print("✅ DOĞRU: Equipment code=1531 updated (100 km)")
else:
    print("❓ Database kontrol edin")
