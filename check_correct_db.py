import sqlite3

db_path = r'c:\Users\fatiherkin\Desktop\bozankaya_ssh_takip\instance\ssh_takip_bozankaya.db'
print(f'Kontrol edilen database: {db_path}')

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check equipment with id=1 or code=1531
cur.execute("SELECT id, equipment_code, current_km FROM equipment WHERE project_code='belgrad' AND (id=1 OR equipment_code=1531) ORDER BY id")

print('\n════════════════════════════════════════')
print('VERİTABANI - Equipment Kayıtları')
print('════════════════════════════════════════')
print(f'{"ID":>5} | {"CODE":>7} | {"KM":>8}')
print('─' * 30)

rows = cur.fetchall()
if not rows:
    print('Kayıt bulunamadı!')
else:
    for row in rows:
        print(f'{row[0]:>5} | {row[1]:>7} | {str(row[2]):>8}')

conn.close()

print('\n════════════════════════════════════════')
print('DURUM DENETIMI:')
print('════════════════════════════════════════')
if rows:
    # Check id=1
    id1_row = [r for r in rows if r[0] == 1]
    # Check code=1531
    code1531_row = [r for r in rows if r[1] == 1531]
    
    if id1_row and id1_row[0][2] == 100:
        print('❌ HATA: Equipment id=1 güncellendi (km=100)')
        print('   Yanlış kayda yazılmış!')
    else:
        print('✅ id=1 güvenli')
    
    if code1531_row and code1531_row[0][2] == 100:
        print('✅ DOĞRU: Equipment code=1531 güncellendi (km=100)')
    elif code1531_row:
        print(f'⚠️  code=1531 var ama km={code1531_row[0][2]}')
    
    if not code1531_row:
        print('❓ code=1531 hiç bulunamadı')
