from models import db, Equipment
from app import create_app

app = create_app()
with app.app_context():
    print("Updating Equipment names to equipment_code only...")
    
    # Update all equipment to use only equipment_code as name
    for tram_id in range(1534, 1556):
        tram_id_str = str(tram_id)
        eq = Equipment.query.filter_by(equipment_code=tram_id_str).first()
        if eq:
            old_name = eq.name
            eq.name = tram_id_str
            print(f"  {tram_id_str}: '{old_name}' -> '{tram_id_str}'")
        else:
            print(f"  {tram_id_str}: NOT FOUND")
    
    db.session.commit()
    print("\n✓ Equipment names updated!")
    
    # Verify
    print("\nVerifying:")
    for eq in Equipment.query.all():
        print(f"  {eq.equipment_code}: {eq.name}")
