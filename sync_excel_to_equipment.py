#!/usr/bin/env python3
"""Sync Excel to Equipment table - Add missing vehicles"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment
from datetime import datetime
import pandas as pd
import os

app = create_app()

with app.app_context():
    project = 'belgrad'
    
    print("\n" + "="*100)
    print("SYNC: Excel -> Equipment Table")
    print("="*100 + "\n")
    
    # 1. Excel'den araçları oku
    veriler_path = os.path.join(app.root_path, 'data', project, 'Veriler.xlsx')
    df = pd.read_excel(veriler_path, sheet_name='Sayfa2', header=0)
    excel_trams = sorted([str(t) for t in df['tram_id'].dropna().unique().tolist()])
    
    print(f"1. EXCEL ({project}/Veriler.xlsx): {len(excel_trams)} araç")
    print(f"   [{excel_trams[0]} ... {excel_trams[-1]}]\n")
    
    # 2. Equipment table'daki araçları oku
    equipment_list = Equipment.query.filter_by(
        project_code=project,
        parent_id=None
    ).order_by(Equipment.equipment_code).all()
    
    db_trams = sorted([eq.equipment_code for eq in equipment_list])
    
    print(f"2. DATABASE: {len(db_trams)} araç")
    print(f"   [{db_trams[0]} ... {db_trams[-1]}]\n")
    
    # 3. Eksik araçları bul
    excel_set = set(excel_trams)
    db_set = set(db_trams)
    
    missing_in_db = excel_set - db_set
    extra_in_db = db_set - excel_set
    
    print(f"3. KARŞILAŞTIRMA:")
    print(f"   Excel'de var, DB'de YOK: {sorted(missing_in_db)}")
    print(f"   DB'de var, Excel'de YOK: {sorted(extra_in_db)}\n")
    
    # 4. Eksik araçları ekle
    if missing_in_db:
        print(f"4. EKLENIYOR: {len(missing_in_db)} araç\n")
        
        for tram_id in sorted(missing_in_db):
            # Var olan bir araçtan template al
            template = Equipment.query.filter_by(
                project_code=project,
                parent_id=None
            ).first()
            
            if template:
                new_equipment = Equipment(
                    equipment_code=tram_id,
                    name=f'Tramvay {tram_id}',
                    project_code=project,
                    parent_id=None,
                    status='aktif',
                    criticality=template.criticality if hasattr(template, 'criticality') else 'medium',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(new_equipment)
                print(f"   ✓ {tram_id} eklendi")
        
        db.session.commit()
        print()
    else:
        print(f"4. Eksik araç yok\n")
    
    # 5. Doğrulama
    print(f"5. DOĞRULAMA:")
    
    updated_equipment = Equipment.query.filter_by(
        project_code=project,
        parent_id=None
    ).order_by(Equipment.equipment_code).all()
    
    updated_db_trams = sorted([eq.equipment_code for eq in updated_equipment])
    
    print(f"   Toplam araç (güncellenmiş): {len(updated_db_trams)}")
    print(f"   [{updated_db_trams[0]} ... {updated_db_trams[-1]}]")
    
    # Excel ile eşleşiyor mu?
    if set(updated_db_trams) == excel_set:
        print(f"   ✓ Excel ve Database SENKRONIZE\n")
    else:
        remaining_diff = excel_set - set(updated_db_trams)
        print(f"   ✗ Hâlâ fark var: {remaining_diff}\n")
    
    print("="*100)
    print("✓ SYNC TAMAMLANDI")
    print("="*100 + "\n")
