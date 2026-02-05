"""
Export butonlarının çalışıp çalışmadığını test et
"""

from app import create_app
from models import Equipment

app = create_app()

print("=" * 70)
print("EXPORT BUTTON TEST")
print("=" * 70)

with app.app_context():
    eq_count = Equipment.query.count()
    print(f"\nEquipment sayısı: {eq_count}")
    
    print("\n✓ Test endpoint'leri (login gerektirmez):")
    print("  GET http://localhost:5000/servis/test/export/comprehensive")
    print("  GET http://localhost:5000/servis/test/export/rootcause")
    print("  GET http://localhost:5000/servis/test/export/daily?tram_id=TRV-001")
    
    print("\n✓ Normal export routes (login gerekli):")
    print("  GET http://localhost:5000/servis/excel/comprehensive-report")
    print("  GET http://localhost:5000/servis/excel/root-cause-report")
    print("  GET http://localhost:5000/servis/excel/daily-report/TRV-001")
    
    print("\n✓ Dashboard (butonlar burada):")
    print("  http://localhost:5000/servis/durumu")
    
    print("\n" + "=" * 70)
    print("Yapılacaklar:")
    print("=" * 70)
    print("1. Flask uygulamasını başlat: python app.py")
    print("2. Test endpoint'ini test et: curl http://localhost:5000/servis/test/export/comprehensive")
    print("3. Tarayıcıda dashboard aç: http://localhost:5000/servis/durumu")
    print("4. Admin ile giriş yap (varsa)")
    print("5. Export butonlarını tıkla")
