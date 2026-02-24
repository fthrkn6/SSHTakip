#!/usr/bin/env python
"""Test KM update process with new KMDataLogger integration"""

from app import create_app
from models import db, Equipment
from utils_km_data_logger import KMDataLogger
import json
import os

app = create_app()

with app.app_context():
    print("\n" + "="*70)
    print("🧪 KM GÜNCELLEME SİSTEMİ TEST")
    print("="*70)
    
    project = 'belgrad'
    tram_id = '1531'
    
    print(f"\n📋 Test Senaryosu:")
    print(f"  - Proje: {project}")
    print(f"  - Araç: {tram_id}")
    print(f"  - Yeni KM: 16000")
    
    # 1. Eski değerleri al
    print(f"\n1️⃣  BAŞLANGIÇ DURUMU")
    print("-"*70)
    
    equipment = Equipment.query.filter_by(equipment_code=tram_id, project_code=project.lower()).first()
    km_logger = KMDataLogger()
    
    old_equipment_km = equipment.current_km if equipment else 'YOK'
    old_logger_km = km_logger.get_latest_km(project, tram_id) or 0
    
    print(f"  Equipment.current_km: {old_equipment_km}")
    print(f"  KMDataLogger.latest: {old_logger_km}")
    
    # 2. KM güncelleme simülasyonu
    print(f"\n2️⃣  KM GÜNCELLEME YÜKSÜMLASYONU")
    print("-"*70)
    
    new_km = 16000
    equipment.current_km = new_km
    
    # KMLogger ile kaydet
    km_logger.log_km_update(
        project_code=project,
        tram_id=tram_id,
        current_km=new_km,
        previous_km=old_logger_km,
        reason='TEST: Güncelleme kontrolü',
        user_id=1
    )
    
    db.session.commit()
    print(f"  ✓ Equipment.current_km ← {new_km}")
    print(f"  ✓ KMDataLogger.log_km_update() → km_log.json")
    
    # 3. Yeni değerleri kontrol et
    print(f"\n3️⃣  GÜNCELLEME SONRASI KONTROL")
    print("-"*70)
    
    # Equipment tablosu (refresh Session'dan)
    db.session.refresh(equipment)
    new_equipment_km = equipment.current_km
    
    # KM Logger
    new_logger_km = km_logger.get_latest_km(project, tram_id) or 0
    
    # km_log.json dosyasını kontrol et
    log_file = os.path.join(os.path.dirname(__file__), 'logs', 'km_history', project, 'km_log.json')
    last_log_entry = None
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
            if logs:
                last_log_entry = logs[-1]
    
    print(f"  Equipment.current_km: {new_equipment_km}")
    print(f"  KMDataLogger.latest: {new_logger_km}")
    print(f"  km_log.json son giriş: {last_log_entry.get('current_km') if last_log_entry else 'YOK'}")
    
    # 4. Tutarlılık kontrolü
    print(f"\n4️⃣  TUTARLILIK KONTROLÜ")
    print("-"*70)
    
    equipment_ok = new_equipment_km == new_km
    logger_ok = new_logger_km == new_km
    log_file_ok = last_log_entry and last_log_entry.get('current_km') == new_km if last_log_entry else False
    
    print(f"  Equipment == {new_km}: {'✅ ' if equipment_ok else '❌ '}{new_equipment_km}")
    print(f"  Logger == {new_km}: {'✅ ' if logger_ok else '❌ '}{new_logger_km}")
    print(f"  Log File == {new_km}: {'✅ ' if log_file_ok else '❌ '}{last_log_entry.get('current_km') if last_log_entry else 'N/A'}")
    
    # 5. Sonuç
    print(f"\n" + "="*70)
    if equipment_ok and logger_ok and log_file_ok:
        print("✅ TEST BAŞARILI - KM VERİLERİ TUTARLI")
    else:
        print("❌ TEST BAŞARISIZ - TUTARSIZlık VAR")
    print("="*70 + "\n")
