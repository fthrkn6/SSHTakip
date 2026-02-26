"""
Test amaçlı - Dashboard arıza kartı için test verileri ekle
"""
from app import app
from models import db, Equipment, Failure, User
from datetime import datetime, timedelta
import random

with app.app_context():
    # Belgrad projesi ekipmanları getir
    equipments = Equipment.query.filter_by(
        project_code='belgrad',
        equipment_type='Tramvay'
    ).limit(5).all()
    
    if not equipments:
        print("[HATA] Belgrad'da Tramvay bulunamadı")
        exit(1)
    
    # Admin user bul
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        print("[HATA] Admin user bulunamadı")
        exit(1)
    
    print(f"\n[TEST] {len(equipments)} araç için arıza ekleniyor...")
    
    # Test arızaları
    failure_types = ['Motor Arızası', 'Elektrik Arızası', 'Fren Arızası', 'Tekerlek Sorunu', 'Kapı Arızası']
    failure_modes = ['Kısa Devre', 'Aşınma', 'Mekanik Hasara', 'Kontrol Sistemi', 'Sensör Arızası']
    
    added_count = 0
    for equipment in equipments:
        # 3-5 arıza ekle
        num_failures = random.randint(3, 5)
        
        for i in range(num_failures):
            try:
                # Eski tarihler - son 30 gün içinde
                days_ago = random.randint(1, 30)
                failure_date = datetime.utcnow() - timedelta(days=days_ago)
                
                failure_code = f"AR-{equipment.equipment_code}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{i}"
                
                failure = Failure(
                    failure_code=failure_code,
                    equipment_id=equipment.id,
                    title=random.choice(failure_types),
                    description=f"{random.choice(failure_modes)} nedeniyle arıza",
                    severity='yuksek' if random.random() > 0.7 else 'orta',
                    failure_type=random.choice(failure_types),
                    failure_mode=random.choice(failure_modes),
                    status='acik',
                    project_code='belgrad',
                    reported_by=admin.id,
                    failure_date=failure_date,
                    detected_date=failure_date,
                    downtime_minutes=random.randint(30, 480)
                )
                
                db.session.add(failure)
                added_count += 1
                
            except Exception as e:
                print(f"[HATA] Arıza ekelenemedi: {e}")
                db.session.rollback()
    
    # Commit
    try:
        db.session.commit()
        print(f"[OK] {added_count} arıza başarıyla eklendi")
        
        # Kontrol et
        total = Failure.query.filter_by(project_code='belgrad', status='acik').count()
        print(f"[OK] Toplam açık arıza: {total}")
        
        # Equipment başına arıza sayısı göster
        for equipment in equipments:
            count = Failure.query.filter_by(equipment_id=equipment.id, status='acik').count()
            print(f"  - {equipment.equipment_code}: {count} arıza")
            
    except Exception as e:
        print(f"[HATA] Commit başarısız: {e}")
        db.session.rollback()
