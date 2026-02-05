from models import db, Equipment, ServiceLog, RootCauseAnalysis, AvailabilityMetrics
from app import create_app
from datetime import datetime, timedelta, date
import random

app = create_app()
with app.app_context():
    print("Creating test data for all 25 Belgrad tramways...")
    
    # Get all equipment
    all_equipment = Equipment.query.all()
    tram_ids = [eq.equipment_code for eq in all_equipment]
    
    print(f"Creating data for {len(tram_ids)} tramways...")
    
    # System definitions
    systems = {
        'Traksiyon': ['Motor', 'Dişli Kutusu', 'Aksı'],
        'Fren': ['Elektrik Fren', 'Mekanik Fren', 'Padlar'],
        'Klima': ['Kompresör', 'Soğutma', 'Hava Dağıtım'],
        'Kapı': ['Kapı 1', 'Kapı 2', 'Kapı Kontrolü'],
        'Elektrik': ['Pantograf', 'Şarj Sistemi', 'Güç Dağıtım']
    }
    
    for tram_id in tram_ids:
        print(f"\n{tram_id}:")
        
        # Generate ServiceLog data (last 60 days)
        log_count = 0
        for days_ago in range(60, 0, -5):  # Every 5 days
            timestamp = datetime.now() - timedelta(days=days_ago)
            sistem = random.choice(list(systems.keys()))
            alt_sistem = random.choice(systems[sistem])
            status = random.choice(['operasyonel', 'bakım', 'arıza', 'servis dışı'])
            duration = random.uniform(1, 8) if status != 'operasyonel' else 0
            
            log = ServiceLog(
                tram_id=tram_id,
                previous_status='operasyonel',
                new_status=status,
                sistem=sistem,
                alt_sistem=alt_sistem,
                reason=f"Rutin {status}" if status == 'bakım' else f"{alt_sistem} sorunu",
                duration_hours=duration,
                log_date=timestamp
            )
            db.session.add(log)
            log_count += 1
        
        print(f"  ✓ Added {log_count} ServiceLog records")
        
        # Generate RootCauseAnalysis data
        rca_count = 0
        for i in range(15):
            sistem = random.choice(list(systems.keys()))
            alt_sistem = random.choice(systems[sistem])
            
            rca = RootCauseAnalysis(
                tram_id=tram_id,
                sistem=sistem,
                alt_sistem=alt_sistem,
                root_cause=f"Wear and tear in {alt_sistem}",
                immediate_cause=f"Component degradation",
                severity=random.choice(['low', 'medium', 'high', 'critical']),
                failure_mode=f"{alt_sistem} failure",
                analysis_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                status=random.choice(['draft', 'submitted', 'approved', 'closed'])
            )
            db.session.add(rca)
            rca_count += 1
        
        print(f"  ✓ Added {rca_count} RootCauseAnalysis records")
        
        # Generate AvailabilityMetrics
        metric_count = 0
        periods = [
            ('Günlük', 1),
            ('Haftalık', 7),
            ('Aylık', 30),
            ('3 Aylık', 90),
            ('6 Aylık', 180),
            ('Yıllık', 365),
            ('total', 365)
        ]
        
        for period_name, days in periods:
            availability = round(random.uniform(75, 98), 2)
            total_h = days * 24
            operational_h = (availability / 100) * total_h
            downtime_h = total_h - operational_h
            
            metric = AvailabilityMetrics(
                tram_id=tram_id,
                metric_date=date.today() - timedelta(days=days//2),
                report_period=period_name,
                total_hours=total_h,
                operational_hours=round(operational_h, 2),
                downtime_hours=round(downtime_h, 2),
                availability_percentage=availability,
                failure_count=random.randint(2, 8)
            )
            db.session.add(metric)
            metric_count += 1
        
        print(f"  ✓ Added {metric_count} AvailabilityMetrics records")
    
    db.session.commit()
    print("\n" + "=" * 80)
    print("✓ Test data created successfully for all tramways!")
    print("=" * 80)
