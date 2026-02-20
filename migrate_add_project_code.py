#!/usr/bin/env python3
"""Database Migration - Add project_code columns to work_orders and maintenance_plans"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
import sqlite3
import os

app = create_app()

# Find database file
db_path = None
if 'SQLALCHEMY_DATABASE_URI' in app.config:
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        db_path = os.path.join(app.root_path, db_uri.replace('sqlite:///', ''))
else:
    # Try common paths
    for possible_path in [
        os.path.join(app.root_path, 'instance', 'bozankaya.db'),
        os.path.join(app.root_path, 'instance', 'ssh_takip_bozankaya.db'),
        'instance/bozankaya.db',
        'instance/ssh_takip_bozankaya.db',
    ]:
        if os.path.exists(possible_path):
            db_path = possible_path
            break

print(f"\n{'='*100}")
print(f"DATABASE MIGRATION - Add project_code columns")
print(f"{'='*100}\n")

if not db_path or not os.path.exists(db_path):
    print(f"ERROR: Database not found")
    print(f"Tried: {db_path}")
    sys.exit(1)

print(f"Database: {db_path}\n")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("1. Checking existing columns...\n")

tables_to_migrate = [
    ('work_orders', 'project_code'),
    ('maintenance_plans', 'project_code'),
]

for table, column in tables_to_migrate:
    try:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = {row[1] for row in cursor.fetchall()}
        
        if column in columns:
            print(f"  ✓ {table}.{column} - ALREADY EXISTS")
        else:
            print(f"  ✗ {table}.{column} - MISSING")
    except Exception as e:
        print(f"  ? Error checking {table}: {e}")

print("\n2. Adding missing columns...\n")

migration_sql = [
    "ALTER TABLE work_orders ADD COLUMN project_code VARCHAR(50) DEFAULT 'belgrad'",
    "ALTER TABLE maintenance_plans ADD COLUMN project_code VARCHAR(50) DEFAULT 'belgrad'",
]

for query in migration_sql:
    try:
        table_name = query.split()[2]
        column_name = query.split()[-3]
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = {row[1] for row in cursor.fetchall()}
        
        if column_name not in columns:
            cursor.execute(query)
            print(f"  ✓ {query}")
        else:
            print(f"  - {table_name}.{column_name} already exists")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            print(f"  - Column already exists (duplicate check)")
        else:
            print(f"  ✗ {str(e)}")

print("\n3. Verifying columns...\n")

for table, column in tables_to_migrate:
    try:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = {row[1] for row in cursor.fetchall()}
        
        if column in columns:
            print(f"  ✓ {table}.{column} - VERIFIED")
        else:
            print(f"  ✗ {table}.{column} - STILL MISSING!")
    except Exception as e:
        print(f"  ? Error: {e}")

conn.commit()
conn.close()

print(f"\n{'='*100}")
print(f"MIGRATION COMPLETE")
print(f"{'='*100}\n")
