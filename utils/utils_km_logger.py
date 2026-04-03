"""
KM Logging Sistemi - Tramvay KM güncellemelerini log klasörüne kaydet
"""
import os
import json
from datetime import datetime
from pathlib import Path

class KMLogger:
    """KM değişikliklerini kayıt altına al"""
    
    def __init__(self, project_code='belgrad'):
        self.project_code = project_code
        self.log_dir = Path(__file__).parent / 'logs' / 'km_logs' / project_code
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.daily_log = self.log_dir / f'km_{datetime.now().strftime("%Y-%m-%d")}.log'
        self.json_log = self.log_dir / f'km_{datetime.now().strftime("%Y-%m-%d")}.json'
    
    def log_km_update(self, tram_id, old_km, new_km, user=None, notes=''):
        """KM değişikliğini kaydet"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Text log
        text_entry = {
            'timestamp': timestamp,
            'tram_id': tram_id,
            'old_km': old_km,
            'new_km': new_km,
            'km_change': new_km - old_km if (old_km and new_km) else 0,
            'user': user or 'system',
            'notes': notes
        }
        
        with open(self.daily_log, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] Tramvay {tram_id}: {old_km} → {new_km} km (+{new_km - old_km if old_km and new_km else 0}) by {user}\n")
            if notes:
                f.write(f"  Notlar: {notes}\n")
        
        # JSON log
        json_entries = {}
        if self.json_log.exists():
            with open(self.json_log, 'r', encoding='utf-8') as f:
                try:
                    json_entries = json.load(f)
                except:
                    json_entries = {}
        
        key = f"{tram_id}_{timestamp.replace(':', '-')}"
        json_entries[key] = text_entry
        
        with open(self.json_log, 'w', encoding='utf-8') as f:
            json.dump(json_entries, f, ensure_ascii=False, indent=2)
        
        print(f"✅ KM Log: Tramvay {tram_id} - {new_km} km kayıtlandı")
    
    def get_daily_summary(self):
        """Günlük KM özeti getir"""
        if not self.json_log.exists():
            return {}
        
        with open(self.json_log, 'r', encoding='utf-8') as f:
            entries = json.load(f)
        
        # Tramvay başına toplam KM
        summary = {}
        for entry in entries.values():
            tram_id = entry['tram_id']
            if tram_id not in summary:
                summary[tram_id] = {
                    'updates': 0,
                    'total_km_added': 0,
                    'latest_km': entry['new_km']
                }
            summary[tram_id]['updates'] += 1
            summary[tram_id]['total_km_added'] += entry['km_change']
            summary[tram_id]['latest_km'] = entry['new_km']
        
        return summary
    
    def get_monthly_report(self, year, month):
        """Aylık rapor getir"""
        month_dir = self.log_dir / f"{year}-{month:02d}"
        
        if not month_dir.exists():
            return {}
        
        all_entries = {}
        for log_file in month_dir.glob('*.json'):
            with open(log_file, 'r', encoding='utf-8') as f:
                entries = json.load(f)
                all_entries.update(entries)
        
        return all_entries

# Flask route'una entegre etmek için helper
def log_km_change(tram_id, old_km, new_km, user=None, project_code='belgrad', notes=''):
    """KM değişikliğini logla"""
    logger = KMLogger(project_code)
    logger.log_km_update(tram_id, old_km, new_km, user, notes)
