#!/usr/bin/env python3
"""Check database schema - Verify project_code columns"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    print("\nDATABASE SCHEMA CHECK\n")
    
    inspector = inspect(db.engine)
    
    tables_to_check = [
        ('work_orders', 'project_code'),
        ('maintenance_plans', 'project_code'),
    ]
    
    all_good = True
    
    for table, column in tables_to_check:
        try:
            columns = {c['name'] for c in inspector.get_columns(table)}
            print(f"{table}: {len(columns)} columns")
            
            if column in columns:
                print(f"  ✓ {column} exists\n")
            else:
                print(f"  ✗ {column} MISSING\n")
                all_good = False
        except Exception as e:
            print(f"{table}: ERROR - {e}\n")
            all_good = False
    
    if all_good:
        print("✓ All required columns present!")
    else:
        print("✗ Some columns are missing - migration failed")
    
    print()
    
    # List all columns in the users table
    users_columns = inspector.get_columns('users')
    
    print("\nUser table columns:")
    print("-" * 60)
    for i, col in enumerate(users_columns, 1):
        col_name = col['name']
        col_type = str(col['type'])
        null = "NULL" if col['nullable'] else "NOT NULL"
        default = f"DEFAULT: {col['default']}" if col['default'] else ""
        print(f"{i:2d}. {col_name:<25} {col_type:<20} {null:<10} {default}")
    
    print("-" * 60)
    print(f"Total: {len(users_columns)} columns")
    
    # Check if assigned_projects exists
    col_names = [c['name'] for c in users_columns]
    if 'assigned_projects' in col_names:
        print("\nOK: assigned_projects column FOUND")
    else:
        print("\nERROR: assigned_projects column NOT FOUND")
        print(f"Available columns: {col_names}")
