#!/usr/bin/env python3
import sqlite3
import os

db_path = 'instance/ssh_takip_bozankaya.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Kontrol: alt_sistem sütunu var mı?
    cursor.execute("PRAGMA table_info(service_status)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'alt_sistem' not in columns:
        # Sütunu ekle
        cursor.execute("ALTER TABLE service_status ADD COLUMN alt_sistem VARCHAR(100) DEFAULT ''")
        conn.commit()
        print("✅ alt_sistem sütunu başarıyla eklendi")
    else:
        print("ℹ️  alt_sistem sütunu zaten mevcut")
    
    conn.close()
    print("✅ Veritabanı güncellendi")
except Exception as e:
    print(f"❌ Hata: {e}")
