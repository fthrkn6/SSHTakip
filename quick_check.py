"""
Basit Test - Veritabanında veri olup olmadığını kontrol et
"""

from app import create_app
from models import Equipment, ServiceLog

app = create_app()

with app.app_context():
    eq_count = Equipment.query.count()
    log_count = ServiceLog.query.count()
    
    print(f"Equipment: {eq_count}")
    print(f"ServiceLog: {log_count}")
    
    if eq_count == 0:
        print("\n❌ Veritabanında araç yok!")
        print("Lütfen araç ekleyin veya test verisi oluşturun:")
        print("  python test_service_status_data.py")
    else:
        print(f"\n✅ {eq_count} araç bulundu")
        
    if log_count == 0:
        print("\n❌ Veritabanında log yok!")
        print("Lütfen test verisi oluşturun:")
        print("  python test_service_status_data.py")
    else:
        print(f"\n✅ {log_count} log bulundu")
