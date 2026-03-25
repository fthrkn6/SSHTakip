"""
Unified KM Data Manager - Tüm uygulamada aynı veri kullanılsın
Equipment tablosu source of truth
km_data.json ise backup/sync için
"""
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Any
from flask import current_app, session

class KMDataManager:
    """KM verilerini yönet - tek kaynaktan oku"""
    
    @staticmethod
    def get_equipment_km(tram_id: str, project_code: Optional[str] = None) -> int:
        """
        Get current KM for tram (from Equipment table)
        PRIMARY SOURCE: Equipment.current_km
        """
        from models import Equipment
        
        equiv = Equipment.query.filter_by(equipment_code=str(tram_id)).first()
        if equiv:
            return equiv.current_km or 0
        return 0
    
    @staticmethod
    def get_all_tram_kms(project_code: Optional[str] = None) -> Dict[str, int]:
        """
        Get KM for all trams (from Equipment table)
        Returns: {tram_id: current_km}
        """
        from models import Equipment
        
        if project_code is None:
            project_code = session.get('current_project', 'belgrad')
        
        equipments = Equipment.query.filter_by(
            parent_id=None,
            project_code=project_code
        ).all()
        
        km_dict = {}
        for eq in equipments:
            km_dict[eq.equipment_code] = eq.current_km or 0
        
        return km_dict
    
    @staticmethod
    def sync_json_to_equipment(project_code='belgrad'):
        """
        km_data.json -> Equipment.current_km senkronize et
        (km_data.json gerçek veriler içeriyor, equipment zeroları olmasın)
        """
        from models import Equipment, db
        
        km_file = Path(current_app.root_path) / 'data' / project_code / 'km_data.json'
        
        if not km_file.exists():
            print(f"Warning: {km_file} bulunamadı")
            return False
        
        try:
            with open(km_file, 'r', encoding='utf-8') as f:
                km_data = json.load(f)
        except Exception as e:
            print(f"Error: km_data.json okuma hatası: {e}")
            return False
        
        updated_count = 0
        for tram_id, km_info in km_data.items():
            try:
                current_km = km_info.get('current_km', 0)
                
                # Equipment'i bul ya da oluştur
                equipment = Equipment.query.filter_by(equipment_code=str(tram_id)).first()
                
                if not equipment:
                    # Oluştur
                    equipment = Equipment(
                        equipment_code=str(tram_id),
                        name=f'Tramvay {tram_id}',
                        equipment_type='Tramway',
                        project_code=project_code,
                        current_km=current_km
                    )
                    db.session.add(equipment)
                else:
                    # Güncelle
                    if equipment.current_km != current_km:
                        equipment.current_km = current_km
                        updated_count += 1
                
                db.session.flush()
            except Exception as e:
                print(f"Error: {tram_id} güncelleme hatası: {e}")
        
        try:
            db.session.commit()
            print(f"OK: km_data.json -> Equipment senkronize edildi ({updated_count} güncelleme)")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error: Commit hatası: {e}")
            return False
    
    @staticmethod
    def validate_km_consistency(project_code='belgrad'):
        """
        Equipment.current_km vs km_data.json tutarlılığını kontrol et
        Returns: {consistent: True/False, mismatches: []}
        """
        # Equipment'ten veriyi al
        equipment_kms = KMDataManager.get_all_tram_kms(project_code)
        
        # km_data.json'u oku
        km_file = Path(current_app.root_path) / 'data' / project_code / 'km_data.json'
        
        if not km_file.exists():
            return {'consistent': True, 'mismatches': [], 'note': 'km_data.json bulunamadı (sorun değil)', 'total_trams': len(equipment_kms)}
        
        try:
            with open(km_file, 'r', encoding='utf-8') as f:
                km_json_data = json.load(f)
        except:
            return {'consistent': False, 'mismatches': [], 'note': 'km_data.json okunamadı', 'total_trams': len(equipment_kms)}
        
        # Karşılaştır
        mismatches = []
        for tram_id, equipment_km in equipment_kms.items():
            json_km = km_json_data.get(str(tram_id), {}).get('current_km', 0)
            if equipment_km != json_km:
                mismatches.append({
                    'tram_id': tram_id,
                    'equipment_km': equipment_km,
                    'json_km': json_km
                })
        
        return {
            'consistent': len(mismatches) == 0,
            'mismatches': mismatches,
            'total_trams': len(equipment_kms)
        }
    
    @staticmethod
    def repair_km_consistency(project_code='belgrad'):
        """
        Tutarlılık sorunlarını düzelt (JSON gerçek veri kaynağı ise JSON -> Equipment)
        """
        return KMDataManager.sync_json_to_equipment(project_code)

# Flask context'ine ek helper
def get_tram_km(tram_id):
    """Tramvay KM'sini getir - Flask route'larında kullan"""
    return KMDataManager.get_equipment_km(tram_id)

def get_all_kms(project_code=None):
    """Tüm KM'leri getir - Flask route'larında kullan"""
    return KMDataManager.get_all_tram_kms(project_code)
