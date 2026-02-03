#!/usr/bin/env python
"""
SQLite migration - Kolonu direkt ekle
"""
import sqlite3
import os

db_path = 'instance/ssh_takip_bozankaya.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Mevcut şemayı kontrol et
    cursor.execute("PRAGMA table_info(equipment)")
    columns = {row[1] for row in cursor.fetchall()}
    
    print(f"Mevcut kolonlar: {columns}")
    
    # Eksik kolonları ekle
    if 'current_km' not in columns:
        cursor.execute("ALTER TABLE equipment ADD COLUMN current_km INTEGER DEFAULT 0")
        print("✅ current_km kolonu eklendi")
    
    if 'monthly_km' not in columns:
        cursor.execute("ALTER TABLE equipment ADD COLUMN monthly_km INTEGER DEFAULT 0")
        print("✅ monthly_km kolonu eklendi")
    
    if 'last_update' not in columns:
        cursor.execute("ALTER TABLE equipment ADD COLUMN last_update DATETIME")
        print("✅ last_update kolonu eklendi")
    
    conn.commit()
    conn.close()
    print("✅ Migration tamamlandı")
else:
    print(f"❌ Veritabanı bulunamadı: {db_path}")

