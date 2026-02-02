"""
Veritabanı migration scripti - interval_km kolonu ekleme
"""
from app import create_app, db

def init_database():
    """Veritabanını yeni şema ile baştan oluştur"""
    app = create_app()
    
    with app.app_context():
        print("Veritabanı oluşturuluyor...")
        db.create_all()
        print("✅ Veritabanı başarıyla oluşturuldu!")
        print("Şimdi 'python create_sample_data.py' komutu ile örnek verileri oluşturabilirsiniz.")

if __name__ == '__main__':
    init_database()
