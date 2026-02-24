"""
Maintenance Data Logger - Her proje için Bakım Planları verilerini logs klasöründe tut
maintenance_history/{project_code}/maintenance_log.json formatında
"""
import os
import json
from datetime import datetime
from pathlib import Path

class MaintenanceDataLogger:
    """Bakım planları verilerini logs klasöründe tut - geçmiş veriler erişilebilir"""
    
    BASE_DIR = 'logs/maintenance_history'
    
    @staticmethod
    def ensure_project_dir(project_code):
        """Her proje için klasör oluştur"""
        project_dir = os.path.join(MaintenanceDataLogger.BASE_DIR, project_code)
        os.makedirs(project_dir, exist_ok=True)
        return project_dir
    
    @staticmethod
    def get_maintenance_file(project_code):
        """Projenin Bakım log dosyasını al"""
        project_dir = MaintenanceDataLogger.ensure_project_dir(project_code)
        return os.path.join(project_dir, 'maintenance_log.json')
    
    @staticmethod
    def log_maintenance_record(project_code, tram_id, plan_name, schedule_km, schedule_hours, 
                               maintenance_type='Preventive', status='Planned', user_id=None):
        """
        Bakım kaydını log'la
        {
            'timestamp': '2026-02-24T10:30:00',
            'tram_id': '1531',
            'plan_name': '6K Service',
            'schedule_km': 6000,
            'schedule_hours': 20,
            'maintenance_type': 'Preventive',
            'status': 'Planned',
            'user_id': 1,
            'project_code': 'belgrad'
        }
        """
        try:
            maintenance_file = MaintenanceDataLogger.get_maintenance_file(project_code)
            
            # Mevcut logu oku
            logs = []
            if os.path.exists(maintenance_file):
                try:
                    with open(maintenance_file, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                except:
                    logs = []
            
            # Yeni kayıt ekle
            new_log = {
                'timestamp': datetime.now().isoformat(),
                'tram_id': str(tram_id),
                'plan_name': plan_name,
                'schedule_km': schedule_km,
                'schedule_hours': schedule_hours,
                'maintenance_type': maintenance_type,
                'status': status,
                'user_id': user_id,
                'project_code': project_code
            }
            logs.append(new_log)
            
            # Dosyaya yaz
            with open(maintenance_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False, default=str)
            
            return True
        except Exception as e:
            print(f"❌ Maintenance log error: {e}")
            return False
    
    @staticmethod
    def get_maintenance_history(project_code, tram_id=None):
        """
        Bakım geçmişini getir
        tram_id verilirse o tramvayın geçmişi, değilse tüm geçmiş
        """
        try:
            maintenance_file = MaintenanceDataLogger.get_maintenance_file(project_code)
            
            if not os.path.exists(maintenance_file):
                return []
            
            with open(maintenance_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            if tram_id:
                logs = [log for log in logs if log['tram_id'] == str(tram_id)]
            
            return sorted(logs, key=lambda x: x['timestamp'], reverse=True)
        except Exception as e:
            print(f"❌ Maintenance history error: {e}")
            return []
    
    @staticmethod
    def get_maintenance_by_plan(project_code, plan_name):
        """
        Belirli bir bakım planının tüm kayıtlarını getir
        """
        try:
            maintenance_file = MaintenanceDataLogger.get_maintenance_file(project_code)
            
            if not os.path.exists(maintenance_file):
                return []
            
            with open(maintenance_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            logs = [log for log in logs if log['plan_name'] == plan_name]
            return sorted(logs, key=lambda x: x['timestamp'], reverse=True)
        except Exception as e:
            print(f"❌ Maintenance by plan error: {e}")
            return []
    
    @staticmethod
    def get_maintenance_statistics(project_code):
        """
        Proje için bakım istatistikleri
        """
        try:
            history = MaintenanceDataLogger.get_maintenance_history(project_code)
            
            stats = {
                'total_records': len(history),
                'by_status': {},
                'by_type': {},
                'by_tram': {}
            }
            
            for log in history:
                status = log.get('status', 'Unknown')
                mtype = log.get('maintenance_type', 'Unknown')
                tram_id = log.get('tram_id', 'Unknown')
                
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                stats['by_type'][mtype] = stats['by_type'].get(mtype, 0) + 1
                stats['by_tram'][tram_id] = stats['by_tram'].get(tram_id, 0) + 1
            
            return stats
        except Exception as e:
            print(f"❌ Maintenance statistics error: {e}")
            return {}
