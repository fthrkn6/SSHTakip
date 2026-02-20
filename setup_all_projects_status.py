#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Her proje için ServiceStatus verisi ekle"""

from app import create_app, db
from models import Equipment, ServiceStatus
from datetime import date

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("📊 HER PROJE İÇİN SERVİS DURUMU EKLE")
    print("="*60)
    
    today = str(date.today())
    projects = ['belgrad', 'kayseri', 'iasi', 'timisoara', 'kocaeli', 'gebze']
    
    # Eski verileri sil
    ServiceStatus.query.delete()
    db.session.commit()
    
    # Her proje için türlü durumlar ekle
    project_data = {
        'belgrad': {
            'count': 8,
            'statuses': ['Servis', 'Servis', 'İşletme Kaynaklı Servis Dışı', 'Servis', 
                        'Servis Dışı', 'Servis', 'Servis', 'Servis']
        },
        'kayseri': {
            'count': 10,
            'statuses': ['Servis', 'Servis', 'İşletme Kaynaklı Servis Dışı', 'Servis', 
                        'Servis', 'Servis Dışı', 'Servis', 'Servis', 'Servis', 'Servis']
        },
        'iasi': {
            'count': 6,
            'statuses': ['Servis', 'Servis', 'Servis', 'Servis Dışı', 'Servis', 'Servis']
        },
        'timisoara': {
            'count': 5,
            'statuses': ['Servis', 'İşletme Kaynaklı Servis Dışı', 'Servis', 'Servis', 'Servis']
        },
        'kocaeli': {
            'count': 7,
            'statuses': ['Servis', 'Servis', 'Servis', 'Servis', 'Servis Dışı', 'Servis', 'Servis']
        },
        'gebze': {
            'count': 4,
            'statuses': ['Servis', 'Servis', 'İşletme Kaynaklı Servis Dışı', 'Servis']
        }
    }
    
    for project in projects:
        print(f"\n🚊 {project.upper()} - ServiceStatus ekleniyor...")
        
        # Bu projenin ekipmanlarını al
        equipment_list = Equipment.query.filter_by(
            project_code=project,
            parent_id=None
        ).all()
        
        if not equipment_list:
            print(f"  ⚠️  Ekipman bulunamadı")
            continue
        
        statuses = project_data.get(project, {}).get('statuses', [])
        
        for i, equipment in enumerate(equipment_list):
            status = statuses[i] if i < len(statuses) else 'Servis'
            
            record = ServiceStatus(
                tram_id=equipment.equipment_code,
                date=today,
                status=status,
                project_code=project
            )
            db.session.add(record)
            print(f"  ✓ {equipment.equipment_code}: {status}")
        
        db.session.commit()
        print(f"  ✅ {len(equipment_list)} ekipman eklendi")
    
    print("\n" + "="*60)
    print("✅ Tüm projeler için ServiceStatus verisi eklendi!")
    print("="*60 + "\n")
