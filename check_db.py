import sqlite3

conn = sqlite3.connect('instance/ssh_takip_bozankaya.db')
cursor = conn.cursor()

# First, list all tables
print("Tables in database:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

# Check admin users
print("\nAdmin Users:")
cursor.execute("SELECT username, role FROM users WHERE role = 'admin'")
admins = cursor.fetchall()
print(f"  Count: {len(admins)}")
for username, role in admins:
    print(f"    - {username} ({role})")

# Check all user roles
print("\nAll User Roles:")
cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
roles = cursor.fetchall()
for role, count in roles:
    print(f"  {role}: {count}")

# Check permissions
print("\nPermissions:")
cursor.execute("SELECT COUNT(*) FROM permission")
perm_count = cursor.fetchone()[0]
print(f"  Total: {perm_count}")

cursor.execute("SELECT COUNT(*) FROM role_permission")
rp_count = cursor.fetchone()[0]
print(f"  Role Permissions: {rp_count}")

conn.close()
