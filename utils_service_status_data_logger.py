"""
Service Status Data Logger - Her proje için Servis Durumu verilerini logs klasöründe tut
service_status_history/{project_code}/service_status_log.json formatında
İki yönlü: Hem ekrana yazılsın, hem log'dan okunabilsin
"""
import os
import json
from datetime import datetime
from pathlib import Path

class ServiceStatusDataLogger:
    """Servis durumu verilerini logs klasöründe tut - geçmiş veriler erişilebilir ve güncellenebilir"""
    
    BASE_DIR = 'logs/service_status_history'
    
    @staticmethod
    def ensure_project_dir(project_code):
        """Her proje için klasör oluştur"""
        project_dir = os.path.join(ServiceStatusDataLogger.BASE_DIR, project_code)
        os.makedirs(project_dir, exist_ok=True)
        return project_dir
    
    @staticmethod
    def get_status_file(project_code):
        """Projenin Servis Durumu log dosyasını al"""
        project_dir = ServiceStatusDataLogger.ensure_project_dir(project_code)
        return os.path.join(project_dir, 'service_status_log.json')
    
    @staticmethod
    def log_status_change(project_code, tram_id, date, status, sistem='', alt_sistem='', 
                         aciklama='', user_id=None):
        """
        Servis durumu değişikliğini log'la
        {
            'timestamp': '2026-02-24T10:30:00',
            'date': '2026-02-24',
            'tram_id': '1531',
            'status': 'Servis',
            'sistem': 'Elektrik',
            'alt_sistem': 'Motor',
            'aciklama': 'Rutin bakım',
            'user_id': 1,
            'project_code': 'belgrad'
        }
        """
        try:
            status_file = ServiceStatusDataLogger.get_status_file(project_code)
            
            # Mevcut logu oku
            logs = []
            if os.path.exists(status_file):
                try:
                    with open(status_file, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                except:
                    logs = []
            
            # Yeni kayıt ekle
            new_log = {
                'timestamp': datetime.now().isoformat(),
                'date': str(date),
                'tram_id': str(tram_id),
                'status': status,
                'sistem': sistem,
                'alt_sistem': alt_sistem,
                'aciklama': aciklama,
                'user_id': user_id,
                'project_code': project_code
            }
            logs.append(new_log)
            
            # Dosyaya yaz
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False, default=str)
            
            return True
        except Exception as e:
            print(f"❌ Service status log error: {e}")
            return False
    
    @staticmethod
    def get_status_history(project_code, tram_id=None, date_from=None, date_to=None):
        """
        Servis durumu geçmişini getir
        tram_id verilirse o tramvayın geçmişi, değilse tüm geçmiş
        date_from ve date_to ile tarih aralığı filtrelenebilir
        """
        try:
            status_file = ServiceStatusDataLogger.get_status_file(project_code)
            
            if not os.path.exists(status_file):
                return []
            
            with open(status_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            if tram_id:
                logs = [log for log in logs if log['tram_id'] == str(tram_id)]
            
            if date_from:
                logs = [log for log in logs if log['date'] >= str(date_from)]
            
            if date_to:
                logs = [log for log in logs if log['date'] <= str(date_to)]
            
            return sorted(logs, key=lambda x: x['timestamp'], reverse=True)
        except Exception as e:
            print(f"❌ Service status history error: {e}")
            return []
    
    @staticmethod
    def get_current_status(project_code, tram_id):
        """
        Tramvayın güncel servis durumunu getir (son kaydı)
        """
        try:
            history = ServiceStatusDataLogger.get_status_history(project_code, tram_id)
            if history:
                return history[0]  # En son (reverse sort olduğu için)
            return None
        except Exception as e:
            print(f"❌ Current status error: {e}")
            return None
    
    @staticmethod
    def get_all_current_statuses(project_code):
        """
        Proje için tüm tramvayların güncel durumlarını getir
        Returns: {tram_id: {'status': '', 'timestamp': ''}}
        """
        try:
            status_file = ServiceStatusDataLogger.get_status_file(project_code)
            
            if not os.path.exists(status_file):
                return {}
            
            with open(status_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # Her tram_id için en son kaydı bul
            current_statuses = {}
            for log in logs:
                tram_id = log['tram_id']
                if tram_id not in current_statuses:  # İlk bulduğumuz en son (çünkü reverse)
                    current_statuses[tram_id] = {
                        'status': log['status'],
                        'timestamp': log['timestamp'],
                        'date': log['date'],
                        'sistem': log.get('sistem', ''),
                        'alt_sistem': log.get('alt_sistem', ''),
                        'aciklama': log.get('aciklama', '')
                    }
            
            return current_statuses
        except Exception as e:
            print(f"❌ All current statuses error: {e}")
            return {}
    
    @staticmethod
    def get_status_distribution(project_code, date=None):
        """
        Belirli bir gün için durumun dağılımını getir
        Returns: {'Servis': 10, 'İşletme': 5, ...}
        """
        try:
            status_file = ServiceStatusDataLogger.get_status_file(project_code)
            
            if not os.path.exists(status_file):
                return {}
            
            with open(status_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            if date:
                logs = [log for log in logs if log['date'] == str(date)]
            
            # Her tram_id için en son durumunu al
            current_statuses = {}
            for log in logs:
                tram_id = log['tram_id']
                if tram_id not in current_statuses:
                    current_statuses[tram_id] = log['status']
            
            # Durum dağılımını hesapla
            distribution = {}
            for status in current_statuses.values():
                distribution[status] = distribution.get(status, 0) + 1
            
            return distribution
        except Exception as e:
            print(f"❌ Status distribution error: {e}")
            return {}
