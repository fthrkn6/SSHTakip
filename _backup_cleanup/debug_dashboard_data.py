#!/usr/bin/env python
# -*- coding: utf-8 -*-
from models import db, Equipment
from app import create_app
import pandas as pd
import os

app = create_app()

with app.app_context():
    current_project = 'belgrad'
    
    # Excel'deki tram_id'leri al
    excel_path = os.path.join(app.root_path, 'data', current_project, 'Veriler.xlsx')
    df = pd.read_excel(excel_path, sheet_name='Sayfa2', header=0)
    excel_tram_ids = df['tram_id'].dropna().unique().tolist()
    excel_tram_ids = [str(int(t)).zfill(3) if isinstance(t, (int, float)) else str(t) for t in excel_tram_ids]
    excel_tram_ids = list(set(excel_tram_ids))
    excel_tram_ids.sort(key=lambda x: int(x) if x.isdigit() else 0)
    
    print(f"Excel tram_ids: {excel_tram_ids[:10]}")
    
    # Database'de bu ID'ler var mı?
    db_trams = Equipment.query.filter(
        Equipment.equipment_code.in_(excel_tram_ids),
        Equipment.parent_id == None,
        Equipment.project_code == current_project
    ).all()
    
    print(f"Found in DB: {len(db_trams)} equipment")
    for t in db_trams:
        print(f"  - {t.equipment_code} | {t.name}")
    
    # Fallback: Database'deki tüm equipment
    print("\n--- ALL DB Equipment for belgrad ---")
    all_equip = Equipment.query.filter_by(parent_id=None, project_code=current_project).all()
    print(f"Total: {len(all_equip)}")
    for t in all_equip:
        print(f"  - {t.equipment_code} | {t.name}")
