import sqlite3

db_path = 'instance/ssh_takip_bozankaya.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all columns in service_status table
cursor.execute("PRAGMA table_info(service_status)")
columns = [col[1] for col in cursor.fetchall()]

print("Current columns in service_status table:")
for col in columns:
    print(f"  - {col}")

if 'alt_sistem' in columns:
    print("\n✅ alt_sistem column EXISTS")
else:
    print("\n❌ alt_sistem column MISSING - adding it now...")
    try:
        cursor.execute("ALTER TABLE service_status ADD COLUMN alt_sistem VARCHAR(100) DEFAULT ''")
        conn.commit()
        print("✅ alt_sistem column added successfully!")
    except Exception as e:
        print(f"❌ Error adding column: {e}")

conn.close()
