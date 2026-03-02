from app import app, db
from models import Equipment

with app.app_context():
    # 4001-4022 araçlarını sil (Excel'de tanımlanmamış, orphan veri)
    to_delete = db.session.query(Equipment).filter(
        Equipment.equipment_code.in_([str(c) for c in range(4001, 4023)])
    ).all()
    
    print(f"Silinecek araçlar: {len(to_delete)}")
    for eq in to_delete[:5]:
        print(f"  - {eq.equipment_code} ({eq.project_code})")
    
    # Sil
    for eq in to_delete:
        db.session.delete(eq)
    
    db.session.commit()
    print(f"\n✓ {len(to_delete)} orphan araç silindi")
    
    # Kontrol
    remaining = db.session.query(Equipment).filter(
        Equipment.equipment_code.in_([str(c) for c in range(4001, 4023)])
    ).count()
    print(f"✓ Kontrol: 4001-4022 artık {remaining} araç kaldı")
