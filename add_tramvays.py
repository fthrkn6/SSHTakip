#!/usr/bin/env python
"""
Tramvay verisi ekle - tüm projeler için
"""
from app import create_app, db
from models import Equipment
from datetime import datetime

def add_tramvays():
    app = create_app()
    
    with app.app_context():
        # Veritabanı tablosunu oluştur
        db.create_all()
        
        # Tüm projeler için tramvay verisi
        projects = {
            'BEL': {'name': 'Belgrad', 'count': 5, 'location': 'Belgrad'},
            'GEB': {'name': 'Gebze', 'count': 3, 'location': 'Gebze'},
            'ISI': {'name': 'Iași', 'count': 4, 'location': 'Iași'},
            'KAY': {'name': 'Kayseri', 'count': 2, 'location': 'Kayseri'},
            'KOC': {'name': 'Kocaeli', 'count': 3, 'location': 'Kocaeli'},
            'TIM': {'name': 'Timișoara', 'count': 2, 'location': 'Timișoara'},
        }
        
        added = 0
        for prefix, proj_info in projects.items():
            for i in range(1, proj_info['count'] + 1):
                code = f'{prefix}-{i:02d}'
                
                # Zaten varsa atla
                existing = Equipment.query.filter_by(equipment_code=code).first()
                if existing:
                    continue
                
                tram = Equipment(
                    equipment_code=code,
                    name=f'{proj_info["name"]} {i}',
                    equipment_type='Tramvay',
                    manufacturer='Siemens',
                    model='Avenio',
                    location=proj_info['location'],
                    status='aktif',
                    criticality='high',
                    current_km=0,
                    monthly_km=0,
                    notes=f'{proj_info["name"]} şehrinde çalışmakta',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(tram)
                added += 1
        
        if added > 0:
            db.session.commit()
            print(f'✅ {added} tramvay başarıyla eklendi')
        else:
            print('ℹ️ Zaten tüm tramvaylar veritabanında mevcut')
        
        # Toplam sayı kontrol et
        total = Equipment.query.filter_by(equipment_type='Tramvay').count()
        print(f'📊 Veritabanında toplam {total} tramvay mevcut')

if __name__ == '__main__':
    add_tramvays()
