#!/usr/bin/env python
"""Equipment tablosunu KMDataLogger verilerigit senkronize et"""

from app import create_app
from models import db, Equipment
from utils_km_data_logger import KMDataLogger
import json
import os

app = create_app()

with app.app_context():
    print("\n" + "="*70)
    print("🔄 EQUIPMENT TABLOSU - KM LOGGER SENKRONİZASYONU")
    print("="*70)
    
    km_logger = KMDataLogger()
    projects = ['belgrad', 'iasi', 'timisoara', 'kayseri', 'kocaeli', 'gebze']
    total_synced = 0
    
    for project in projects:
        print(f"\n📁 {project.upper()} PROJESI")
        print("-"*70)
        
        # Bu projekteki araçları getir
        equipments = Equipment.query.filter_by(project_code=project.lower()).all()
        print(f"  Toplam araç: {len(equipments)}")
        
        synced = 0
        for eq in equipments:
            tram_id = str(eq.equipment_code)
            
            # KM Logger'dan KM al
            latest_km = km_logger.get_latest_km(project, tram_id)
            
            if latest_km and latest_km > 0:
                old_km = eq.current_km or 0
                eq.current_km = latest_km
                synced += 1
                
                if synced <= 3:  # İlk 3'ü göster
                    print(f"  ✓ {tram_id}: {old_km} → {latest_km} km")
        
        if synced > 3:
            print(f"  + {synced - 3} araç daha senkronize edildi (gösterilmiyor)")
        
        print(f"  ✓ {synced}/{len(equipments)} araç senkronize")
        total_synced += synced
    
    # Değişiklikleri kaydet
    print(f"\n💾 Veritabanına kaydediliyor...")
    db.session.commit()
    
    print(f"\n" + "="*70)
    print(f"✅ SENKRONİZASYON TAMAMLANDI")
    print(f"   Toplam senkronize araç: {total_synced}")
    print("="*70 + "\n")
