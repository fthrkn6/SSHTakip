#!/usr/bin/env python3
"""Belgrad Projesi - Araç Verileri Nereden Çekiliyor?"""
import sys
sys.path.insert(0, '.')

from app import create_app
from models import Equipment, ServiceStatus, AvailabilityMetrics
from datetime import date
import json

app = create_app()

with app.app_context():
    print("\n" + "="*100)
    print("🚊 BELGRAD PROJESİ - ARAÇ VERİLERİ AKIŞI")
    print("="*100)
    
    project = 'belgrad'
    today = str(date.today())
    
    print("\n1️⃣  EQUIPMENT TABLE (Araç Ana Verileri)")
    print("-" * 100)
    print("""
SELECT * FROM equipment 
WHERE project_code='belgrad' AND parent_id IS NULL
ORDER BY equipment_code
    """)
    
    equipment_list = Equipment.query.filter_by(
        project_code=project,
        parent_id=None
    ).order_by(Equipment.equipment_code).all()
    
    print(f"\n📊 Sonuç: {len(equipment_list)} Araç")
    print("\nJSON Format:")
    eq_data = []
    for i, eq in enumerate(equipment_list[:3], 1):
        eq_dict = {
            'id': eq.id,
            'equipment_code': eq.equipment_code,
            'name': eq.name,
            'project_code': eq.project_code,
            'location': eq.location if hasattr(eq, 'location') else '',
            'status': eq.status if hasattr(eq, 'status') else ''
        }
        eq_data.append(eq_dict)
        print(json.dumps(eq_dict, indent=2, ensure_ascii=False))
    if len(equipment_list) > 3:
        print(f"... ve {len(equipment_list)-3} daha")
    
    print("\n" + "-"*100)
    print("2️⃣  SERVICE STATUS TABLE (Bugünün Durum Verileri)")
    print("-" * 100)
    print(f"""
SELECT * FROM service_status 
WHERE project_code='belgrad' 
  AND date='{today}'
  AND tram_id IN (1531, 1532, 1533, ...)
    """)
    
    service_status_list = ServiceStatus.query.filter_by(
        project_code=project,
        date=today
    ).limit(3).all()
    
    print(f"\n📊 Sonuç: {len(service_status_list)} Kayıt (İlk 3)")
    print("\nJSON Format:")
    for ss in service_status_list:
        ss_dict = {
            'id': ss.id,
            'tram_id': ss.tram_id,
            'date': ss.date,
            'status': ss.status,
            'system': ss.system if hasattr(ss, 'system') else '',
            'subsystem': ss.subsystem if hasattr(ss, 'subsystem') else '',
            'project_code': ss.project_code
        }
        print(json.dumps(ss_dict, indent=2, ensure_ascii=False))
    
    print("\n" + "-"*100)
    print("3️⃣  AVAILABILITY METRICS TABLE (Kullanılabilirlik Metrikleri)")
    print("-" * 100)
    print(f"""
SELECT * FROM availability_metrics 
ORDER BY metric_date DESC
LIMIT 3
    """)
    
    metrics_list = AvailabilityMetrics.query.order_by(
        AvailabilityMetrics.metric_date.desc()
    ).limit(3).all()
    
    print(f"\n📊 Sonuç: {len(metrics_list)} Kayıt (Son 3)")
    if len(metrics_list) > 0:
        print("\nJSON Format:")
        for m in metrics_list:
            m_dict = {
                'id': m.id,
                'tram_id': m.tram_id,
                'metric_date': str(m.metric_date),
                'availability_percentage': m.availability_percentage,
                'downtime_hours': m.downtime_hours,
                'project_code': m.project_code
            }
            print(json.dumps(m_dict, indent=2, ensure_ascii=False))
    else:
        print("\n📊 Sonuç: Hiç Metriks Yok")
    
    print("\n" + "="*100)
    print("📋 ÖZET - ARAÇ VERİLERİ NEREDEN ÇEKİLİYOR")
    print("="*100)
    print(f"""
🛢️  DATABASE (SQLite)
├─ equipment (25 araç ana verileri)
│  └─ SELECT * WHERE project_code='belgrad' AND parent_id IS NULL
│     → ID, equipment_code, name, location, status ...
│
├─ service_status (Bugünün durum verileri)
│  └─ SELECT * WHERE project_code='belgrad' AND date='{today}'
│     → tram_id, status (Aktif/Servis Dışı/İşletme), system, subsystem ...
│
└─ availability_metrics (Metrikleri)
   └─ SELECT * WHERE project_code='belgrad' ORDER BY metric_date DESC
      → availability_percentage, downtime_hours ...

📄 EXCEL (Veriler.xlsx)
└─ data/belgrad/Veriler.xlsx
   Sayfa2 → tram_id sütunu → 25 araç
   
🔄 ENTEGRASYON
└─ Dashboard açıldığında:
   1. Equipment tablosundan 25 araç oku
   2. Her araç için ServiceStatus'ten bugünün durumu sor
   3. Availability Metrics'ten son verileri al
   4. Hesaplama yap (Stats: aktif, arıza, maintenance, availability%)
   5. Tarayıcıya gönder
""")
    print("="*100 + "\n")
