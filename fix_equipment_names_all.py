from models import db, Equipment
from app import create_app

app = create_app()
with app.app_context():
    print("Updating 1531, 1532, 1533 names...")
    
    for tram_id in ['1531', '1532', '1533']:
        eq = Equipment.query.filter_by(equipment_code=tram_id).first()
        if eq:
            old_name = eq.name
            eq.name = tram_id
            print(f"  {tram_id}: '{old_name}' -> '{tram_id}'")
    
    db.session.commit()
    print("\n✓ Updated!")
    
    print("\nVerifying all:")
    for eq in Equipment.query.all():
        print(f"  {eq.equipment_code}: {eq.name}")
