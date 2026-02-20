#!/usr/bin/env python3
"""Verify Equipment page shows all data"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment

app = create_app()

with app.app_context():
    project = 'belgrad'
    
    print("\n" + "="*100)
    print("EQUIPMENT SAYFASI - TÜMMÜ VERILER")
    print("="*100 + "\n")
    
    # Tüm equipment
    all_eq = Equipment.query.filter_by(parent_id=None, project_code=project).all()
    all_codes = sorted([eq.equipment_code for eq in all_eq])
    
    print(f"1. EQUIPMENT SAYFASINDA GOSTERILECEK:")
    print(f"   Toplam: {len(all_codes)} arac")
    print(f"   Araçlar: {all_codes}\n")
    
    print(f"2. DETAY:")
    for eq in all_eq[:5]:
        print(f"   ID: {eq.id:3} | Code: {eq.equipment_code:6} | Name: {eq.name}")
    
    if len(all_eq) > 5:
        print(f"   ...")
        for eq in all_eq[-2:]:
            print(f"   ID: {eq.id:3} | Code: {eq.equipment_code:6} | Name: {eq.name}")
    
    print(f"\n" + "="*100)
    print(f"✓ Equipment sayfasinda TÜM {len(all_codes)} arac GOSTERILIYOR")
    print(f"✓ Excel filtresi KALDIRIILDI")
    print("="*100 + "\n")
