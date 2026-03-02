from app import app, db
from models import Equipment

with app.app_context():
    # 4001-4022 Database'de var mı?
    check_4001_4022 = db.session.query(Equipment).filter(
        Equipment.equipment_code.in_([str(c) for c in range(4001, 4023)])
    ).with_entities(Equipment.equipment_code, Equipment.project_code).all()
    
    print(f"4001-4022 Database'de: {len(check_4001_4022)} araç")
    if check_4001_4022:
        for code, proj in check_4001_4022[:5]:
            print(f"  {code}: {proj}")
        print(f"  ... ({len(check_4001_4022)} total)")
    
    # Tüm Database Equipment'leri göster
    all_eqs = db.session.query(Equipment.equipment_code, Equipment.project_code).all()
    print(f"\nToplam Equipment: {len(all_eqs)}")
    
    # Proje bazlı sayım
    from sqlalchemy import func
    counts = db.session.query(Equipment.project_code, func.count()).group_by(Equipment.project_code).all()
    print("\nProject_code dağılımı:")
    for p, c in counts:
        print(f"  {p}: {c}")
