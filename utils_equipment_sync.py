"""
Excel ve Database senkronizasyonu
Excel Sayfa2'deki araç listesi Database'deki Equipment tablosuyla eşitlenir
"""

import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

def sync_equipment_with_excel(project_code: str) -> Tuple[int, int]:
    """
    Excel Sayfa2 ile Database Equipment tablosunu senkronize et
    
    - Excel'de olan araçlar Database'de olmalı
    - Database'de olan ama Excel'de olmayan silinmeli
    - Otomatik olarak her API çağrısında çalışacak
    """
    try:
        from app import db
        from models import Equipment
        from utils_project_excel_store import get_tramvay_list_with_km
        # Excel'den araçları oku
        excel_equipments = get_tramvay_list_with_km(project_code)
        excel_codes = set([eq.equipment_code for eq in excel_equipments])
        
        # Database'den araçları oku
        db_equipments = Equipment.query.filter_by(project_code=project_code).all()
        db_codes = set([eq.equipment_code for eq in db_equipments])
        
        # Silinecekler (Database'de ama Excel'de olmayan)
        to_delete = db_codes - excel_codes
        
        # Eklenecekler (Excel'de ama Database'de olmayan)
        to_add = excel_codes - db_codes
        
        # Silme işlemi
        for code in to_delete:
            eq = Equipment.query.filter_by(equipment_code=code, project_code=project_code).first()
            if eq:
                db.session.delete(eq)
                logger.info(f"[SYNC] Silindi: {project_code}/{code}")
        
        # Ekleme işlemi (Excel'deki objelerden kopyala)
        for excel_eq in excel_equipments:
            if excel_eq.equipment_code in to_add:
                new_eq = Equipment(
                    equipment_code=excel_eq.equipment_code,
                    project_code=project_code,
                    equipment_type=excel_eq.equipment_type,
                    equipment_name=excel_eq.equipment_name,
                    km_current=excel_eq.km_current,
                    km_target=excel_eq.km_target,
                    maintenance_status=excel_eq.maintenance_status
                )
                db.session.add(new_eq)
                logger.info(f"[SYNC] Eklendi: {project_code}/{excel_eq.equipment_code}")
        
        db.session.commit()
        
        if to_delete or to_add:
            logger.info(f"[SYNC] {project_code}: Silindi={len(to_delete)}, Eklendi={len(to_add)}")
        
        return {
            'synced': True,
            'deleted': len(to_delete),
            'added': len(to_add)
        }
    
    except Exception as e:
        logger.error(f"[SYNC] Error syncing {project_code}: {e}")
        db.session.rollback()
        return {
            'synced': False,
            'error': str(e)
        }


if __name__ == '__main__':
    # Test kodu
    print("= Equipment Sync Test =")
    print("Senkronizasyon fonksiyonu Flask uygulaması içinde çalışır")
