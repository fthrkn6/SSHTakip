#!/usr/bin/env python
# coding: utf-8
"""
Veriler.xlsx'te olmayan araçları Equipment'ten temizle
"""
from models import db, Equipment
from app import create_app
from routes.service_status import get_tram_ids_from_veriler

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        # Geçerli tram_id'ler (Veriler.xlsx'ten)
        current_project = 'belgrad'
        valid_ids = get_tram_ids_from_veriler(current_project)
        valid_ids_set = set(valid_ids)
        
        print(f"[INFO] Veriler.xlsx'te {len(valid_ids)} tram bulundu")
        print(f"[INFO] Veriler.xlsx tram'ları: {valid_ids}")
        
        # Equipment'te olmayan araçları bul
        all_equipment = Equipment.query.filter_by(project_code=current_project, parent_id=None).all()
        extra_equipment = [e for e in all_equipment if e.equipment_code not in valid_ids_set]
        
        print(f"\n[INFO] Equipment'te {len(all_equipment)} araç var")
        print(f"[INFO] Silinecek {len(extra_equipment)} araç:")
        for e in extra_equipment:
            print(f"  - {e.equipment_code} ({e.name})")
        
        # Sil
        if extra_equipment:
            for e in extra_equipment:
                db.session.delete(e)
            
            db.session.commit()
            print(f"\n[OK] {len(extra_equipment)} araç silindi")
        else:
            print("\n[OK] Silinecek araç yok")
        
        # Sonuç
        remaining = Equipment.query.filter_by(project_code=current_project, parent_id=None).count()
        print(f"[FINAL] Equipment'te kalan: {remaining} araç")
        
        # Veriler ile karşılaştır
        equipment_codes = {e.equipment_code for e in Equipment.query.filter_by(project_code=current_project, parent_id=None).all()}
        overlap = equipment_codes & valid_ids_set
        print(f"[VERIFICATION] Veriler.xlsx ve Equipment'te ortak: {len(overlap)} araç")
