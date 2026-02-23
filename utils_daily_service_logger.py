"""
Günlük Servis Durumu Logu - Tüm servis durum değişikliklerini kaydet
Her gün otomatik özet raporunu oluştur
"""
import os
import json
from datetime import datetime, date
from pathlib import Path
import csv

class DailyServiceLogger:
    """Günlük servis durumunu logla ve raporla"""
    
    def __init__(self, project_code='belgrad'):
        self.project_code = project_code
        self.log_dir = Path(__file__).parent / 'logs' / 'daily_service' / project_code
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.daily_date = date.today()
        self.daily_log = self.log_dir / f'service_{self.daily_date.strftime("%Y-%m-%d")}.json'
        self.summary_log = self.log_dir / f'summary_{self.daily_date.strftime("%Y-%m-%d")}.csv'
    
    def log_status_change(self, tram_id, status, sistem='', alt_sistem='', aciklama='', user=None):
        """Servis durumu değişikliğini kaydet"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = {
            'timestamp': timestamp,
            'tram_id': tram_id,
            'status': status,
            'sistem': sistem,
            'alt_sistem': alt_sistem,
            'aciklama': aciklama,
            'user': user or 'system'
        }
        
        # JSON logunu güncelle
        entries = {}
        if self.daily_log.exists():
            with open(self.daily_log, 'r', encoding='utf-8') as f:
                try:
                    entries = json.load(f)
                except:
                    entries = {}
        
        key = f"{tram_id}_{timestamp.replace(':', '-').replace(' ', '_')}"
        entries[key] = entry
        
        with open(self.daily_log, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Servis Log: {tram_id} - {status}")
    
    def generate_daily_summary(self):
        """Günlük özet raporunu oluştur"""
        if not self.daily_log.exists():
            return None
        
        with open(self.daily_log, 'r', encoding='utf-8') as f:
            entries = json.load(f)
        
        # Özet istatistikleri
        status_counts = {}
        sistem_counts = {}
        alt_sistem_counts = {}
        
        for entry in entries.values():
            status = entry.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            sistem = entry.get('sistem', 'Tanımlanmamış')
            sistem_counts[sistem] = sistem_counts.get(sistem, 0) + 1
            
            alt_sistem = entry.get('alt_sistem', '-')
            if alt_sistem:
                alt_sistem_counts[alt_sistem] = alt_sistem_counts.get(alt_sistem, 0) + 1
        
        summary = {
            'date': str(self.daily_date),
            'timestamp_generated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_entries': len(entries),
            'status_breakdown': status_counts,
            'sistem_breakdown': sistem_counts,
            'alt_sistem_breakdown': alt_sistem_counts,
            'entries': entries
        }
        
        # CSV ye de yaz (kolay okuma için)
        with open(self.summary_log, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Tramvay', 'Durum', 'Sistem', 'Alt Sistem', 'Açıklama', 'Saat', 'Kullanıcı'])
            writer.writeheader()
            for entry in entries.values():
                writer.writerow({
                    'Tramvay': entry['tram_id'],
                    'Durum': entry['status'],
                    'Sistem': entry['sistem'],
                    'Alt Sistem': entry['alt_sistem'],
                    'Açıklama': entry['aciklama'],
                    'Saat': entry['timestamp'],
                    'Kullanıcı': entry['user']
                })
        
        return summary
    
    def get_daily_stats(self):
        """Günlük istatistikleri getir"""
        summary = self.generate_daily_summary()
        if not summary:
            return {}
        
        return {
            'total_updates': summary['total_entries'],
            'statuses': summary['status_breakdown'],
            'systems': summary['sistem_breakdown'],
            'subsystems': summary['alt_sistem_breakdown']
        }

# Flask route'una entegre için helper
def log_service_status(tram_id, status, sistem='', alt_sistem='', aciklama='', user=None, project_code='belgrad'):
    """Servis durumunu logla"""
    logger = DailyServiceLogger(project_code)
    logger.log_status_change(tram_id, status, sistem, alt_sistem, aciklama, user)
    return logger.generate_daily_summary()
