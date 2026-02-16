#!/usr/bin/env python
# -*- coding: utf-8 -*-
from models import db, Equipment
from app import create_app

app = create_app()

with app.app_context():
    trams = Equipment.query.filter(
        Equipment.project_code == 'belgrad',
        Equipment.parent_id == None
    ).order_by(Equipment.equipment_code).limit(20).all()
    
    print(f"Total Equipment records: {len(trams)}")
    print("Equipment codes:")
    for t in trams:
        print(f"  - {t.equipment_code} | Name: {t.name} | Current KM: {t.current_km}")
