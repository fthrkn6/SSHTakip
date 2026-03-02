from app import app, db
from models import Equipment

with app.app_context():
    # 2001-2017 araçları sil
    orphan_codes = list(range(2001, 2018))  # 2001-2017
    
    to_delete = Equipment.query.filter(Equipment.equipment_code.in_([str(c) for c in orphan_codes])).all()
    
    print(f"Silinecek orphan araçlar: {len(to_delete)}")
    for eq in to_delete:
        print(f"  - {eq.equipment_code} (project: {eq.project_code})")
    
    for eq in to_delete:
        db.session.delete(eq)
    
    db.session.commit()
    print(f"\n✓ {len(to_delete)} orphan araç silindi")
