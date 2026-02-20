#!/usr/bin/env python3
"""Add ServiceStatus record for newly added vehicle"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import ServiceStatus, Equipment
from datetime import datetime
import pytz

app = create_app()

with app.app_context():
    project = 'belgrad'
    tram_id = '1557'
    
    print("\n" + "="*100)
    print("ADD: ServiceStatus Record for 1557")
    print("="*100 + "\n")
    
    # 1. Equipment'ı bul
    equipment = Equipment.query.filter_by(
        equipment_code=tram_id,
        project_code=project,
        parent_id=None
    ).first()
    
    if not equipment:
        print(f"✗ Equipment {tram_id} bulunamadı!")
        sys.exit(1)
    
    print(f"1. Equipment bulunamadı: {equipment.equipment_code} ({equipment.name})\n")
    
    # 2. Bugünün kaydını kontrol et
    from datetime import date
    today_str = date.today().strftime('%Y-%m-%d')
    
    existing = ServiceStatus.query.filter_by(
        tram_id=tram_id,
        project_code=project,
        date=today_str
    ).first()
    
    if existing:
        print(f"2. Bugünün kaydı VAR - Atlanıyor\n")
    else:
        # 3. Yeni kayıt oluştur
        new_record = ServiceStatus(
            tram_id=tram_id,
            project_code=project,
            date=today_str,
            status='İşletme',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(new_record)
        db.session.commit()
        
        print(f"2. Yeni ServiceStatus kaydı oluşturuldu")
        print(f"   - Date: {today_str}")
        print(f"   - Tram ID: {tram_id}")
        print(f"   - Status: İşletme\n")
    
    # 4. Doğrulama
    print(f"3. DOĞRULAMA:")
    
    status_records = ServiceStatus.query.filter_by(
        tram_id=tram_id,
        project_code=project
    ).count()
    
    print(f"   Toplam ServiceStatus kayıtları: {status_records}")
    print(f"   Son kayıt tarihi: {today_str}\n")
    
    print("="*100)
    print("✓ SERVICESTATUS EKLENDI")
    print("="*100 + "\n")
