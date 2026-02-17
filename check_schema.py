#!/usr/bin/env python
"""Check database schema"""

from app import create_app
from models import db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    
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
