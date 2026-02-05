"""
Create test data for Service Status system
"""

from app import create_app, db
from models import Equipment, ServiceLog, AvailabilityMetrics, User, RootCauseAnalysis
from datetime import datetime, timedelta, date
import random

app = create_app()

with app.app_context():
    # Create admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@test.com', full_name='Admin User')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin user created")
    
    # Get equipment list
    equipments = Equipment.query.limit(5).all()
    if not equipments:
        print("⚠️ No equipment found! Skipping test data creation")
    else:
        print(f"✓ Found {len(equipments)} equipment items")
        
        # Systems and subsystems
        systems = ['Elektrik', 'Mekanik', 'HVAC', 'Kapı', 'Traksiyon']
        subsystems = {
            'Elektrik': ['Pantograf', 'Muling', 'Kontrol'],
            'Mekanik': ['Tekerlek', 'Fren', 'Aks'],
            'HVAC': ['Kompressor', 'Fan', 'Filtre'],
            'Kapı': ['Kapı Motor', 'Sensör', 'Kontrol'],
            'Traksiyon': ['Motor', 'Redüktör', 'Kopling']
        }
        
        # Create test data for each equipment
        for eq in equipments:
            tram_id = eq.equipment_code  # Use equipment_code as tram_id
            print(f"\n  Creating data for {tram_id}...")
            
            # Create 10 service logs over last 30 days
            for i in range(10):
                log_date = datetime.now() - timedelta(days=random.randint(0, 30))
                sistem = random.choice(systems)
                log = ServiceLog(
                    tram_id=tram_id,
                    log_date=log_date,
                    previous_status='operasyonel',
                    new_status=random.choice(['operasyonel', 'bakımda', 'arızalı']),
                    sistem=sistem,
                    alt_sistem=random.choice(subsystems.get(sistem, ['Bilinmiyor'])),
                    duration_hours=random.uniform(0.5, 8),
                    reason=f'Test log {i+1}',
                    created_by=admin.id
                )
                db.session.add(log)
            
            # Create daily metrics for last 7 days
            for i in range(7):
                metric_date = date.today() - timedelta(days=i)
                metric = AvailabilityMetrics(
                    tram_id=tram_id,
                    metric_date=metric_date,
                    availability_percentage=random.uniform(85, 99),
                    operational_hours=random.uniform(18, 23),
                    downtime_hours=random.uniform(1, 6),
                    maintenance_hours=random.uniform(0, 3),
                    mtbf_hours=random.uniform(100, 500),
                    mttr_hours=random.uniform(1, 8),
                    mttm_hours=random.uniform(1, 5),
                    report_period='Günlük'
                )
                db.session.add(metric)
            
            # Create weekly metric
            metric = AvailabilityMetrics(
                tram_id=tram_id,
                metric_date=date.today() - timedelta(days=7),
                availability_percentage=random.uniform(85, 99),
                operational_hours=random.uniform(150, 165),
                downtime_hours=random.uniform(10, 30),
                maintenance_hours=random.uniform(0, 10),
                report_period='Haftalık'
            )
            db.session.add(metric)
            
            # Create monthly metric
            metric = AvailabilityMetrics(
                tram_id=tram_id,
                metric_date=date.today() - timedelta(days=30),
                availability_percentage=random.uniform(80, 99),
                operational_hours=random.uniform(600, 720),
                downtime_hours=random.uniform(30, 120),
                report_period='Aylık'
            )
            db.session.add(metric)
            
            # Create root cause analyses
            for i in range(3):
                sistem = random.choice(systems)
                rca = RootCauseAnalysis(
                    tram_id=tram_id,
                    sistem=sistem,
                    alt_sistem=random.choice(subsystems.get(sistem, ['Bilinmiyor'])),
                    root_cause=f'Test root cause {i+1}',
                    severity=random.choice(['low', 'medium', 'high', 'critical']),
                    failure_mode=f'Failure mode {i+1}',
                    status='submitted'
                )
                db.session.add(rca)
        
        db.session.commit()
        
        # Verify data creation
        print("\n" + "="*60)
        print("DATA CREATION SUMMARY:")
        print("="*60)
        print(f"ServiceLog records: {ServiceLog.query.count()}")
        print(f"AvailabilityMetrics records: {AvailabilityMetrics.query.count()}")
        print(f"RootCauseAnalysis records: {RootCauseAnalysis.query.count()}")
        print("✓ Test data created successfully!")
