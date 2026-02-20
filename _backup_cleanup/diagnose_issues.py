#!/usr/bin/env python3
"""Sorunları teşhis et"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment, ServiceStatus
from datetime import date
import json

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("🔍 SORUN TEŞHISI")
    print("="*80)
    
    # ===== SORUN 1: Dashboard'da 50 gösteriliyor =====
    print("\n1️⃣  DASHBOARD: Araç Sayısı Kontrolü")
    print("-" * 80)
    
    belgrad_eq = Equipment.query.filter_by(
        project_code='belgrad',
        parent_id=None
    ).all()
    
    print(f"Total Equipment (parent_id=None): {len(belgrad_eq)}")
    print(f"Equipment'lerin parent_id değerleri:")
    parent_counts = {}
    for eq in belgrad_eq[:5]:
        print(f"  - {eq.equipment_code}: parent_id={eq.parent_id}")
    
    # Parent ID'lere göre grup
    with_parent = Equipment.query.filter_by(project_code='belgrad').filter(
        Equipment.parent_id != None
    ).count()
    without_parent = Equipment.query.filter_by(
        project_code='belgrad',
        parent_id=None
    ).count()
    
    print(f"\nBelgrad Equipment Analiz:")
    print(f"  ├─ parent_id=None: {without_parent}")
    print(f"  ├─ parent_id!=NULL: {with_parent}")
    print(f"  └─ TOPLAM: {without_parent + with_parent}")
    
    # ===== SORUN 2: Servis Durumu Sayfası 0 Gösteriliyor =====
    print("\n2️⃣  SERVIS DURUMU: Veri Akış Kontrolü")
    print("-" * 80)
    
    today = str(date.today())
    
    # Test: /servis/durumu/tablo endpoint
    with app.test_client() as client:
        # Session oluştur
        with client.session_transaction() as sess:
            from models import User
            test_user = User.query.filter_by(email='test@test.com').first()
            if test_user:
                sess['_user_id'] = str(test_user.id)
                sess['current_project'] = 'belgrad'
        
        # Fetch et
        response = client.get('/servis/durumu/tablo')
        print(f"Endpoint Response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            stats = data.get('stats', {})
            table_data = data.get('table_data', [])
            
            print(f"\nResponse Format:")
            print(f"  ├─ stats.operational: {stats.get('operational')}")
            print(f"  ├─ stats.maintenance: {stats.get('maintenance')}")
            print(f"  ├─ stats.outofservice: {stats.get('outofservice')}")
            print(f"  ├─ stats.total: {stats.get('total')}")
            print(f"  ├─ stats.availability: {stats.get('availability')}")
            print(f"  └─ table_data rows: {len(table_data)}")
            
            if len(table_data) > 0:
                print(f"\nİlk 3 kayıt:")
                for item in table_data[:3]:
                    print(f"  - {item['tram_id']}: {item['status']}")
    
    # ===== SORUN 3: ServiceStatus Tablosunda Ne Var =====
    print("\n3️⃣  SERVICESTATUS: Veri Kontrolü")
    print("-" * 80)
    
    belgrad_status = ServiceStatus.query.filter_by(
        project_code='belgrad',
        date=today
    ).all()
    
    print(f"Bugün Belgrad ServiceStatus Kayıtları: {len(belgrad_status)}")
    
    if len(belgrad_status) > 0:
        print(f"İlk 5 kayıt:")
        for status in belgrad_status[:5]:
            print(f"  - {status.tram_id}: {status.status}")
    else:
        print(f"⚠️  Bugün için ServiceStatus kaydı yok!")
    
    # ===== ÖNERİLER =====
    print("\n" + "="*80)
    print("💡 ÖNERILER")
    print("="*80)
    
    if len(belgrad_eq) == 50:
        print(f"✅ Parent_id kontrolünü yapan filter doğru\n")
    
    if len(belgrad_status) == 0:
        print(f"❌ ServiceStatus'te bugün için veri yok! Test ET!\n")
    else:
        print(f"✅ ServiceStatus'te veri var\n")
    
    print("="*80 + "\n")
