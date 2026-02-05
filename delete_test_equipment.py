from models import db, Equipment
from app import create_app

app = create_app()
with app.app_context():
    print("=" * 80)
    print("DELETING TEST/EXTRA EQUIPMENT")
    print("=" * 80)
    
    # Equipment codes to delete
    to_delete = [
        'BEL-01', 'BEL-02', 'BEL-03', 'BEL-04', 'BEL-05',
        'GEB-01', 'GEB-02', 'GEB-03',
        'ISI-01', 'ISI-02', 'ISI-03', 'ISI-04',
        'KAY-01', 'KAY-02',
        'KOC-01', 'KOC-02', 'KOC-03',
        'TEST-001',
        'TIM-01', 'TIM-02',
        'TRV-001', 'TRV-002', 'TRV-003', 'TRV-004', 'TRV-005',
        'TRV-006', 'TRV-007', 'TRV-008', 'TRV-009', 'TRV-010',
        'TRV-001-BOG1', 'TRV-001-BOG2',
        'TRV-001-BRAKE',
        'TRV-001-DOOR1', 'TRV-001-DOOR2',
        'TRV-001-HVAC',
        'TRV-001-MOTOR',
        'TRV-001-PANTO'
    ]
    
    deleted_count = 0
    for tram_id in to_delete:
        eq = Equipment.query.filter_by(equipment_code=tram_id).first()
        if eq:
            print(f"Deleting: {tram_id} - {eq.name}")
            db.session.delete(eq)
            deleted_count += 1
        else:
            print(f"Not found: {tram_id}")
    
    print("\n" + "=" * 80)
    print(f"Total deleted: {deleted_count} records")
    print("=" * 80)
    
    db.session.commit()
    print("\n✓ Veritabanı güncellendi!")
    
    # Verify remaining equipment
    remaining = Equipment.query.all()
    print(f"\nRemaining equipment in database: {len(remaining)}")
    print("\nKalan tramvaylar (Belgrad projesi):")
    for eq in remaining:
        print(f"  - {eq.equipment_code}: {eq.name}")
