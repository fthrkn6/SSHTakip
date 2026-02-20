#!/usr/bin/env python3
"""Check Equipment locations"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment

app = create_app()

with app.app_context():
    project = 'belgrad'
    
    print("\n" + "="*100)
    print("EQUIPMENT KONUMLARI")
    print("="*100 + "\n")
    
    equipment_list = Equipment.query.filter_by(project_code=project).all()
    
    print(f"Toplam: {len(equipment_list)} equipment\n")
    
    print(f"1. KONUM DEGERLERI (distinct):")
    locations = set()
    for eq in equipment_list:
        if eq.location:
            locations.add(eq.location)
    
    if locations:
        for loc in sorted(locations):
            count = sum(1 for eq in equipment_list if eq.location == loc)
            print(f"   - {loc:30} | {count} adet")
    else:
        print(f"   (Konum bilgisi yok)")
    
    print(f"\n2. ORNEKLER:")
    for eq in equipment_list[:10]:
        print(f"   Code: {eq.equipment_code:6} | Location: {eq.location if eq.location else 'YOK'}")
    
    print(f"\n" + "="*100)
    print("Konumlar neresinden gelmeliydi? (data/belgrad/Veriler.xlsx'de location var mı?)")
    print("="*100 + "\n")
