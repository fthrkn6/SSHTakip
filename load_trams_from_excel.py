#!/usr/bin/env python
# -*- coding: utf-8 -*-
from models import db, Equipment
from app import create_app
import pandas as pd
import os

app = create_app()

with app.app_context():
    current_project = 'belgrad'
    
    # Excel'den tram_id'leri al
    excel_path = os.path.join(app.root_path, 'data', current_project, 'Veriler.xlsx')
    df = pd.read_excel(excel_path, sheet_name='Sayfa2', header=0)
    
    tram_ids = df['tram_id'].dropna().unique().tolist()
    
    print(f"Loading {len(tram_ids)} tram IDs from Excel...")
    
    added_count = 0
    for tram_id in tram_ids:
        tram_id_str = str(int(tram_id)).zfill(3)
        
        # Önceden var mı kontrol et
        existing = Equipment.query.filter_by(
            equipment_code=tram_id_str,
            project_code=current_project
        ).first()
        
        if not existing:
            # Yeni Equipment ekle
            equipment = Equipment(
                equipment_code=tram_id_str,
                name=f'Tramvay {tram_id_str}',
                equipment_type='Tramvay',
                project_code=current_project,
                parent_id=None,
                current_km=0,
                total_km=0,
                status='Servis'
            )
            db.session.add(equipment)
            added_count += 1
            print(f"  + {tram_id_str} - Tramvay {tram_id_str}")
    
    db.session.commit()
    print(f"\n✅ {added_count} yeni araç eklendi!")
    
    # Kontrol et
    all_trams = Equipment.query.filter_by(
        project_code=current_project,
        parent_id=None
    ).order_by(Equipment.equipment_code).all()
    
    print(f"\nTotal equipment in {current_project}: {len(all_trams)}")
    for t in all_trams:
        print(f"  - {t.equipment_code} ({t.name})")
