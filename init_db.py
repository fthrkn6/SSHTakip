"""
Database initialization and migration - Create/update database schema
"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from sqlalchemy import text, inspect

def init_and_migrate():
    """Initialize database and apply migrations"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*100)
        print("DATABASE INITIALIZATION & MIGRATION")
        print("="*100 + "\n")
        
        # Step 1: Create all tables
        print("1. Creating database tables...")
        try:
            db.create_all()
            print("   ✓ Database tables created/verified\n")
        except Exception as e:
            print(f"   Error: {e}\n")
        
        # Step 2: Add missing columns
        print("2. Adding missing columns (project_code)...\n")
        
        inspector = inspect(db.engine)
        
        migrations = [
            ('work_orders', 'project_code', "VARCHAR(50) DEFAULT 'belgrad'"),
            ('maintenance_plans', 'project_code', "VARCHAR(50) DEFAULT 'belgrad'"),
        ]
        
        for table_name, col_name, col_type in migrations:
            try:
                # Check if column exists
                columns = {c['name'] for c in inspector.get_columns(table_name)}
                
                if col_name not in columns:
                    # Add the column
                    sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"
                    print(f"   [SQL] {sql}")
                    db.session.execute(text(sql))
                    db.session.commit()
                    print(f"   ✓ Added {table_name}.{col_name}")
                else:
                    print(f"   - {table_name}.{col_name} already exists")
            except Exception as e:
                if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"   - {table_name}.{col_name} already exists")
                else:
                    print(f"   ✗ {table_name}.{col_name}: {e}")
        
        # Step 3: Verify
        print("\n3. Verifying schema...\n")
        
        for table_name, col_name, _ in migrations:
            try:
                columns = {c['name'] for c in inspector.get_columns(table_name)}
                if col_name in columns:
                    print(f"   ✓ {table_name}.{col_name}")
                else:
                    print(f"   ✗ {table_name}.{col_name} MISSING!")
            except Exception as e:
                print(f"   ? {table_name}: {e}")
        
        print("\n" + "="*100)
        print("DATABASE READY")
        print("="*100 + "\n")

if __name__ == '__main__':
    init_and_migrate()
