"""
KMDataManager'da filter sorunu çöz
"""
from app import create_app
from models import db, Equipment

app = create_app()

with app.app_context():
    from flask import session
    
    # session ortamını simule et
    with app.test_request_context():
        # Default session'a belgrad koy
        session['current_project'] = 'belgrad'
        
        print("[DEBUG] equipment_code types:")
        eq = Equipment.query.filter_by(equipment_code='1531').first()
        if eq:
            print(f"  equipment_code value: '{eq.equipment_code}'")
            print(f"  equipment_code type: {type(eq.equipment_code)}")
        
        print("\n[DEBUG] Filter test:")
        result = Equipment.query.filter_by(
            parent_id=None,
            project_code='belgrad'
        ).all()
        
        print(f"  Total equipment with parent_id=None and project='belgrad': {len(result)}")
        for r in result[:3]:
            print(f"  - {r.equipment_code} (current_km={r.current_km})")
        
        # KMDataManager test
        from utils_km_manager import KMDataManager
        km_data = KMDataManager.get_all_tram_kms('belgrad')
        print(f"\n[TEST] get_all_tram_kms('belgrad') returned:")
        print(f"  Total items: {len(km_data)}")
        for k, v in list(km_data.items())[:5]:
            print(f"  {k}: {v} km")
