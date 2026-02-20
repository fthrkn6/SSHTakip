"""
Add assigned_projects column if missing
"""
from app import create_app
from models import db
import sqlite3

def add_missing_column():
    """Add assigned_projects column to users table if missing"""
    app = create_app()
    
    with app.app_context():
        # Try to add column using raw SQL
        try:
            db.session.execute(db.text("""
                ALTER TABLE users ADD COLUMN assigned_projects TEXT
            """))
            db.session.commit()
            print("✓ assigned_projects column added successfully")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print("✓ assigned_projects column already exists")
            else:
                print(f"Note: {str(e)}")
        
        # Verify
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        users_columns = [c['name'] for c in inspector.get_columns('users')]
        
        if 'assigned_projects' in users_columns:
            print("✓ Verification successful - assigned_projects column is in database")
        else:
            print("✗ FAILED - assigned_projects column still missing")
        
        print(f"✓ User table has {len(users_columns)} columns total")

if __name__ == '__main__':
    add_missing_column()
