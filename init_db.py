"""
Veritabanı initialize script - Yeni şema ile database oluştur
"""
from app import create_app
from models import db
import os

def init_database():
    """Veritabanını yeni şema ile oluştur"""
    app = create_app()
    
    with app.app_context():
        print("Veritabanı oluşturuluyor...")
        db.create_all()
        print("OK Database tables created successfully")
        
        # Verify the schema
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        users_columns = [c['name'] for c in inspector.get_columns('users')]
        if 'assigned_projects' in users_columns:
            print("OK assigned_projects column exists")
        else:
            print("ERROR assigned_projects column missing!")
        
        print(f"OK User table has {len(users_columns)} columns")

if os.path.exists('ssh_takip_bozankaya.db'):
    print("OK Database file created: ssh_takip_bozankaya.db")
    file_size = os.path.getsize('ssh_takip_bozankaya.db')
    print(f"OK Database file size: {file_size} bytes")

if __name__ == '__main__':
    init_database()
