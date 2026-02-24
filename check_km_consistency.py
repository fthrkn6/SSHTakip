#!/usr/bin/env python
"""KM veri tutarlılığını kontrol et"""

from app import create_app
from models import db, Equipment
import json
import os

app = create_app()

with app.app_context():
    print("\n" + "="*70)
    print("🔍 KM VERİ KONTROL SİSTEMİ")
    print("="*70)
    
    # 1. Equipment tablosunu kontrol et
    print("\n1️⃣  EQUIPMENT TABLOSU ARACı KONTROLÜ")
    print("-"*70)
    
    equipments = Equipment.query.all()
    print(f"Toplam araç: {len(equipments)}")
    
    # 1531e arayalım
    tram_1531 = Equipment.query.filter_by(equipment_code='1531').first()
    if tram_1531:
        print(f"\n✓ 1531 bulundu:")
        print(f"  - ID: {tram_1531.id}")
        print(f"  - equipment_code: {tram_1531.equipment_code}")
        print(f"  - name: {tram_1531.name}")
        print(f"  - current_km: {tram_1531.current_km}")
        print(f"  - project_code: '{tram_1531.project_code}'")  # FARKLı CASE'leri görmek için quotes
        print(f"  - equipment_type: {tram_1531.equipment_type}")
    else:
        print(f"\n✗ 1531 bulunamadı!")
    
    # Tüm project_code'ları kontrol et
    print(f"\n📊 Equipment tablosundaki tüm project_code'lar:")
    project_codes = set()
    for eq in equipments:
        project_codes.add(eq.project_code)
    for pc in sorted(project_codes):
        count = Equipment.query.filter_by(project_code=pc).count()
        print(f"  - '{pc}': {count} araç")
    
    # 2. KM data files
    print("\n2️⃣  KM VERİ DOSYALARI")
    print("-"*70)
    
    projects = ['belgrad', 'iasi', 'timisoara', 'kayseri', 'kocaeli', 'gebze']
    for project in projects:
        km_file = os.path.join(os.path.dirname(__file__), 'data', project, 'km_data.json')
        km_logger_file = os.path.join(os.path.dirname(__file__), 'logs', 'km_history', project, 'km_log.json')
        
        print(f"\n📁 {project.upper()}:")
        
        # km_data.json
        if os.path.exists(km_file):
            try:
                with open(km_file, 'r', encoding='utf-8') as f:
                    km_data = json.load(f)
                print(f"  ✓ km_data.json: {len(km_data)} araç")
                
                if '1531' in km_data:
                    print(f"    - 1531: {km_data['1531']}")
                else:
                    print(f"    - 1531: YOKED")
            except Exception as e:
                print(f"  ✗ km_data.json hata: {e}")
        else:
            print(f"  - km_data.json: YOK")
        
        # KM Logger file
        if os.path.exists(km_logger_file):
            try:
                with open(km_logger_file, 'r', encoding='utf-8') as f:
                    km_log = json.load(f)
                print(f"  ✓ km_log.json: {len(km_log)} kayıt")
                
                for log in km_log[-2:]:  # Son 2 kaydı göster
                    if log.get('tram_id') == '1531':
                        print(f"    - SON: {log}")
                        break
            except Exception as e:
                print(f"  ✗ km_log.json hata: {e}")
        else:
            print(f"  - km_log.json: YOK")
    
    # 3. Maintenance verileri
    print("\n3️⃣  BAKIM VERİLERİ")
    print("-"*70)
    
    maint_file = os.path.join(os.path.dirname(__file__), 'data', 'belgrad', 'maintenance.json')
    if os.path.exists(maint_file):
        with open(maint_file, 'r', encoding='utf-8') as f:
            maint_data = json.load(f)
        print(f"✓ maintenance.json bulundu: {len(maint_data)} seviye")
    else:
        print(f"✗ maintenance.json bulunamadı: {maint_file}")
    
    print("\n" + "="*70)
    print("✅ KONTROL TAMAMLANDI")
    print("="*70 + "\n")
