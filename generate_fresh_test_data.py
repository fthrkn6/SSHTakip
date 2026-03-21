#!/usr/bin/env python3
"""
Test Data Generator - Güncel Tarihlerle
Tüm projeler için fresh test data oluştur
- Tarihler: Bugünden geriye 30 gün
- Durum verileri: Random mix (✓/✗/⚠)
"""

from app import app, db
from models import Equipment, ServiceStatus
from utils_excel_grid_manager import ExcelGridManager
from datetime import date, timedelta
import random

PROJECTS = ['belgrad', 'istanbul', 'ankara', 'iasi', 'timisoara', 'kayseri', 'kocaeli', 'gebze', 'samsun']

def generate_fresh_test_data():
    with app.app_context():
        print("=" * 70)
        print("🔄 FRESH TEST DATA GENERATOR")
        print("=" * 70)
        
        today = date.today()
        
        for project_code in PROJECTS:
            print(f"\n📍 {project_code.upper()}")
            print("-" * 70)
            
            # Proje'nin araçlarını al
            equipment_list = Equipment.query.filter_by(project_code=project_code, parent_id=None).all()
            equipment_codes = [eq.equipment_code for eq in equipment_list]
            
            if not equipment_codes:
                print(f"  ⚠️ Equipment bulunamadı, skip")
                continue
            
            print(f"  Araçlar: {equipment_codes}")
            
            # Grid Manager'ı hazırla
            grid_manager = ExcelGridManager(project_code)
            
            # Excel Grid'i başlat
            grid_path = grid_manager.init_grid(app.root_path, equipment_codes)
            print(f"  ✓ Grid oluşturuldu: {grid_path}")
            
            # Son 30 günün test data'sını üret
            updates = []
            status_options = [
                ('aktif', '✓'),
                ('servis_disi', '✗'),
                ('isletme_kaynakli', '⚠')
            ]
            
            for day_offset in range(30):  # Son 30 gün
                current_date = today - timedelta(days=day_offset)
                date_str = current_date.strftime('%Y-%m-%d')
                
                for tram_id in equipment_codes:
                    # Random durum seç (70% aktif, 20% servisdışı, 10% işletme)
                    rnd = random.random()
                    if rnd < 0.7:
                        status_code = 'aktif'
                    elif rnd < 0.9:
                        status_code = 'servis_disi'
                    else:
                        status_code = 'isletme_kaynakli'
                    
                    updates.append({
                        'tram_id': tram_id,
                        'date': date_str,
                        'status': status_code
                    })
                    
                    # DB'ye de kaydet (ServiceStatus)
                    existing = ServiceStatus.query.filter_by(
                        project_code=project_code,
                        tram_id=tram_id,
                        date=date_str
                    ).first()
                    
                    if not existing:
                        status_text = {
                            'aktif': 'Servis',
                            'servis_disi': 'Servis Dışı',
                            'isletme_kaynakli': 'İşletme Kaynaklı Servis Dışı'
                        }[status_code]
                        
                        service_status = ServiceStatus(
                            tram_id=tram_id,
                            date=date_str,
                            status=status_text,
                            project_code=project_code
                        )
                        db.session.add(service_status)
            
            # Batch güncelleme
            grid_manager.batch_update_status(app.root_path, updates)
            print(f"  ✓ {len(updates)} veri satırı yazıldı")
        
        # DB'ye commit et
        db.session.commit()
        
        print("\n" + "=" * 70)
        print("✅ TEST DATA OLUŞTURMA TAMAMLANDI")
        print("=" * 70)
        print(f"Tarih Aralığı: {today - timedelta(days=29)} ~ {today}")
        print(f"Durum Dağılımı: 70% ✓ | 20% ✗ | 10% ⚠")

if __name__ == '__main__':
    generate_fresh_test_data()
