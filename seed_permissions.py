"""Seed permission data directly to SQLite database"""
import sqlite3
import os

db_path = 'bozankaya_ssh.db'

if not os.path.exists(db_path):
    print(f"Database not found: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Permission verilerini tanımla
permissions = [
    ('dashboard', 'Gösterge Paneli', '/dashboard'),
    ('ariza_listesi', 'Arıza Listesi', '/ariza-listesi'),
    ('bakim_plani', 'Bakım Planları', '/bakim-plani'),
    ('yedek_parca', 'Yedek Parça', '/yedek-parca'),
    ('fracas', 'FRACAS Analiz', '/fracas'),
    ('kpi', 'KPI Dashboard', '/kpi'),
    ('kullanicilar', 'Kullanıcı Yönetimi', '/kullanicilar'),
    ('yetkilendirme', 'Yetki Yönetimi', '/admin/yetkilendirme'),
    ('admin_panel', 'Admin Paneli', '/admin'),
]

print("Permission tablolarına veri ekleniyor...\n")

# 1. Permission'ları ekle
for page_name, display_name, url in permissions:
    cursor.execute(
        "INSERT OR REPLACE INTO permission (page_name, display_name, url) VALUES (?, ?, ?)",
        (page_name, display_name, url)
    )
    print(f"✓ {display_name}")

conn.commit()

# 2. RolePermission'ları ekle
# Admin: tüm izinleri var
# Manager: çoğu izin var
# Saha: sınırlı izin

# Mevcut permission ID'lerini almak
cursor.execute("SELECT id, page_name FROM permission")
perms = {row[1]: row[0] for row in cursor.fetchall()}

# Mevcut role_permission kayıtlarını sil
cursor.execute("DELETE FROM role_permission")

role_perms = {
    'admin': list(perms.values()),  # Tüm permission'lar
    'manager': [
        perms.get('dashboard'),
        perms.get('ariza_listesi'),
        perms.get('bakim_plani'),
        perms.get('fracas'),
        perms.get('kpi'),
        perms.get('kullanicilar'),
    ],
    'saha': [
        perms.get('dashboard'),
        perms.get('ariza_listesi'),
        perms.get('bakim_plani'),
    ]
}

print("\nRol İzinleri ekleniyor...\n")

for role, perm_ids in role_perms.items():
    for perm_id in perm_ids:
        if perm_id:
            cursor.execute(
                "INSERT INTO role_permission (role, permission_id) VALUES (?, ?)",
                (role, perm_id)
            )
    print(f"✓ {role.upper()}: {len([p for p in perm_ids if p])} izin")

conn.commit()

# 3. Final check
cursor.execute("SELECT COUNT(*) FROM permission")
perm_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM role_permission")
rp_count = cursor.fetchone()[0]

print("\n" + "="*50)
print(f"Permission: {perm_count}")
print(f"RolePermission: {rp_count}")
print("="*50)

conn.close()
print("\n✓ Permission verileri başarıyla eklendi!")
