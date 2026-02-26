import sqlite3

db_path = 'instance/ssh_takip_bozankaya.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Clear old data
cursor.execute("DELETE FROM role_permission WHERE role IN ('admin', 'manager', 'saha') AND page_name IN ('dashboard', 'ariza_listesi', 'bakim_plani', 'yedek_parca', 'fracas', 'kpi', 'kullanicilar', 'yetkilendirme', 'admin_panel')")
conn.commit()
print("[OK] Old data cleared")

# Define permissions
permissions = [
    'dashboard',
    'ariza_listesi',
    'bakim_plani',
    'yedek_parca',
    'fracas',
    'kpi',
    'kullanicilar',
    'yetkilendirme',
    'admin_panel',
]

# Define role permissions (page_name based)
role_perms = {
    'admin': permissions,  # All
    'manager': [
        'dashboard',
        'ariza_listesi',
        'bakim_plani',
        'fracas',
        'kpi',
        'kullanicilar',
    ],
    'saha': [
        'dashboard',
        'ariza_listesi',
        'bakim_plani',
    ]
}

# Insert role permissions
for role, page_names in role_perms.items():
    for page_name in page_names:
        cursor.execute(
            "INSERT OR REPLACE INTO role_permission (role, page_name, can_view, can_edit, can_delete) VALUES (?, ?, ?, ?, ?)",
            (role, page_name, 1, 1, 0)  # All can view, most can edit, none can delete
        )

conn.commit()
print("[OK] Role permissions inserted")

# Verify
cursor.execute("SELECT COUNT(*) FROM role_permission WHERE role IN ('admin', 'manager', 'saha')")
rp_count = cursor.fetchone()[0]

print(f"\n[FINAL] Role Permissions: {rp_count}")

cursor.execute("SELECT role, COUNT(*) FROM role_permission WHERE role IN ('admin', 'manager', 'saha') GROUP BY role")
for role, count in cursor.fetchall():
    print(f"        {role}: {count}")

# Show sample
cursor.execute("SELECT role, page_name FROM role_permission WHERE role = 'admin' LIMIT 3")
print("\n[SAMPLE] Admin permissions:")
for role, page_name in cursor.fetchall():
    print(f"        {page_name}")

conn.close()
print("\n[DONE]")
