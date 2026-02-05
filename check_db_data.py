from models import db, Equipment, AvailabilityMetrics, ServiceLog
from app import create_app

app = create_app()
with app.app_context():
    print("=" * 60)
    print("DATABASE CHECK")
    print("=" * 60)
    
    eq_count = Equipment.query.count()
    print(f"\nEquipment count: {eq_count}")
    print("Equipment list:")
    for eq in Equipment.query.all():
        print(f"  - {eq.equipment_code}: {eq.name} (ID: {eq.id})")
    
    metrics_count = AvailabilityMetrics.query.count()
    print(f"\nAvailabilityMetrics count: {metrics_count}")
    if metrics_count > 0:
        print("Sample metrics:")
        for metric in AvailabilityMetrics.query.limit(5).all():
            print(f"  - {metric.tram_id}: {metric.availability_percentage}% ({metric.report_period})")
    
    logs_count = ServiceLog.query.count()
    print(f"\nServiceLog count: {logs_count}")
    if logs_count > 0:
        print("Sample logs:")
        for log in ServiceLog.query.limit(5).all():
            print(f"  - {log.equipment_id}: {log.status} on {log.timestamp}")
