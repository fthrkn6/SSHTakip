"""Arıza verilerini kontrol et"""
from app import app
from models import db, Failure, Equipment

with app.app_context():
    count = Failure.query.filter_by(project_code='belgrad', status='acik').count()
    print(f"Toplam açık arıza (belgrad): {count}")
    
    if count == 0:
        print("[HATA] Arıza verisi bulunamadı!")
        print("\nTüm arızaları kontrol et:")
        all_count = Failure.query.count()
        print(f"Tüm arızalar: {all_count}")
        all_failures = Failure.query.limit(10).all()
        for f in all_failures:
            print(f"  - {f.failure_code}: status={f.status}, project={f.project_code}")
    else:
        print(f"\n✓ Veriler mevcut. Son 5 arıza:")
        failures = Failure.query.filter_by(project_code='belgrad', status='acik').order_by(Failure.failure_date.desc()).limit(5).all()
        for f in failures:
            eq_code = f.equipment.equipment_code if f.equipment else "N/A"
            print(f"  - {f.failure_code} ({eq_code}): {f.title}")
