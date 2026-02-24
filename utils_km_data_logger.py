"""
KM Data Logger - Her proje için KM verilerini logs klasöründe tut
km_history/{project_code}/km_log.json formatında
"""
import os
import json
from datetime import datetime
from pathlib import Path

class KMDataLogger:
    """KM verilerini logs klasöründe tut - geçmiş veriler erişilebilir"""
    
    BASE_DIR = 'logs/km_history'
    
    @staticmethod
    def ensure_project_dir(project_code):
        """Her proje için klasör oluştur"""
        project_dir = os.path.join(KMDataLogger.BASE_DIR, project_code)
        os.makedirs(project_dir, exist_ok=True)
        return project_dir
    
    @staticmethod
    def get_km_file(project_code):
        """Projenin KM log dosyasını al"""
        project_dir = KMDataLogger.ensure_project_dir(project_code)
        return os.path.join(project_dir, 'km_log.json')
    
    @staticmethod
    def log_km_update(project_code, tram_id, current_km, previous_km=None, reason='', user_id=None):
        """
        KM güncellemesini log'la
        {
            'timestamp': '2026-02-24T10:30:00',
            'tram_id': '1531',
            'previous_km': 15000,
            'current_km': 15050,
            'km_difference': 50,
            'reason': 'Günlük servis',
            'user_id': 1,
            'project_code': 'belgrad'
        }
        """
        try:
            km_file = KMDataLogger.get_km_file(project_code)
            
            # Mevcut logu oku
            logs = []
            if os.path.exists(km_file):
                try:
                    with open(km_file, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                except:
                    logs = []
            
            # Yeni kayıt ekle
            new_log = {
                'timestamp': datetime.now().isoformat(),
                'tram_id': str(tram_id),
                'previous_km': previous_km,
                'current_km': current_km,
                'km_difference': current_km - previous_km if previous_km else 0,
                'reason': reason,
                'user_id': user_id,
                'project_code': project_code
            }
            logs.append(new_log)
            
            # Dosyaya yaz
            with open(km_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False, default=str)
            
            return True
        except Exception as e:
            print(f"❌ KM log error: {e}")
            return False
    
    @staticmethod
    def get_km_history(project_code, tram_id=None):
        """
        KM geçmişini getir
        tram_id verilirse o tramvayın geçmişi, değilse tüm geçmiş
        """
        try:
            km_file = KMDataLogger.get_km_file(project_code)
            
            if not os.path.exists(km_file):
                return []
            
            with open(km_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            if tram_id:
                logs = [log for log in logs if log['tram_id'] == str(tram_id)]
            
            return sorted(logs, key=lambda x: x['timestamp'], reverse=True)
        except Exception as e:
            print(f"❌ KM history error: {e}")
            return []
    
    @staticmethod
    def get_latest_km(project_code, tram_id):
        """
        Tramvayın son KM değerini getir
        Tüm log dosyasından en son kaydı bul
        """
        history = KMDataLogger.get_km_history(project_code, tram_id)
        if history:
            return history[0]['current_km']  # En son (reverse sort olduğu için)
        return 0
    
    @staticmethod
    def get_all_latest_kms(project_code):
        """
        Proje için tüm tramvayların son KM'lerini getir
        Returns: {tram_id: current_km}
        """
        try:
            km_file = KMDataLogger.get_km_file(project_code)
            
            if not os.path.exists(km_file):
                return {}
            
            with open(km_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # Her tram_id için en son kaydı bul
            latest_kms = {}
            for log in logs:
                tram_id = log['tram_id']
                if tram_id not in latest_kms:
                    latest_kms[tram_id] = log['current_km']
            
            return latest_kms
        except Exception as e:
            print(f"❌ Latest KMs error: {e}")
            return {}
