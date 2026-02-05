"""
Export Route Test - Debug ve kontrol
"""

import sys
sys.path.insert(0, '/Users/ferki/Desktop/bozankaya_ssh_takip')

from app import create_app
from models import Equipment, AvailabilityMetrics, RootCauseAnalysis, ServiceLog

app = create_app()

with app.app_context():
    print("=" * 60)
    print("EXPORT ROUTE DEBUG")
    print("=" * 60)
    
    # 1. Equipment kontrol
    equipment_count = Equipment.query.count()
    print(f"\n✓ Equipment sayısı: {equipment_count}")
    
    if equipment_count > 0:
        equipments = Equipment.query.all()
        print(f"\nEquipment listesi:")
        for eq in equipments[:5]:
            print(f"  - Code: {eq.equipment_code}, Name: {eq.name}")
    else:
        print("  ⚠️ Hiç equipment yok!")
    
    # 2. ServiceLog kontrol
    log_count = ServiceLog.query.count()
    print(f"\n✓ ServiceLog sayısı: {log_count}")
    
    if log_count > 0:
        recent_logs = ServiceLog.query.order_by(ServiceLog.log_date.desc()).limit(3).all()
        print(f"\nSon ServiceLog'lar:")
        for log in recent_logs:
            print(f"  - Tram: {log.tram_id}, Status: {log.new_status}")
    else:
        print("  ⚠️ Hiç log yok!")
    
    # 3. AvailabilityMetrics kontrol
    metric_count = AvailabilityMetrics.query.count()
    print(f"\n✓ AvailabilityMetrics sayısı: {metric_count}")
    
    if metric_count > 0:
        metrics = AvailabilityMetrics.query.order_by(AvailabilityMetrics.created_at.desc()).limit(3).all()
        print(f"\nSon Metrics'ler:")
        for m in metrics:
            print(f"  - Tram: {m.tram_id}, Availability: {m.availability_percentage}%")
    else:
        print("  ⚠️ Hiç metric yok!")
    
    # 4. RootCauseAnalysis kontrol
    rca_count = RootCauseAnalysis.query.count()
    print(f"\n✓ RootCauseAnalysis sayısı: {rca_count}")
    
    if rca_count > 0:
        rcas = RootCauseAnalysis.query.limit(3).all()
        print(f"\nSon RCA'lar:")
        for rca in rcas:
            print(f"  - Tram: {rca.tram_id}, Sistem: {rca.sistem}")
    else:
        print("  ⚠️ Hiç RCA yok!")
    
    # 5. Route'ları test et
    print("\n" + "=" * 60)
    print("ROUTE TEST")
    print("=" * 60)
    
    with app.test_client() as client:
        print("\n1. Testing /servis/excel/comprehensive-report")
        try:
            response = client.get('/servis/excel/comprehensive-report')
            print(f"   Status: {response.status_code}")
            if response.status_code != 200:
                print(f"   Error: {response.get_json()}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print("\n2. Testing /servis/excel/root-cause-report")
        try:
            response = client.get('/servis/excel/root-cause-report')
            print(f"   Status: {response.status_code}")
            if response.status_code != 200:
                print(f"   Error: {response.get_json()}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        if equipment_count > 0:
            first_eq = Equipment.query.first()
            print(f"\n3. Testing /servis/excel/daily-report/{first_eq.equipment_code}")
            try:
                response = client.get(f'/servis/excel/daily-report/{first_eq.equipment_code}')
                print(f"   Status: {response.status_code}")
                if response.status_code != 200:
                    print(f"   Error: {response.get_json()}")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ TEST TAMAMLANDI")
    print("=" * 60)
