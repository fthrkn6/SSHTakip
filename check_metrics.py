from models import db, AvailabilityMetrics
from app import create_app
from datetime import datetime

app = create_app()
with app.app_context():
    print("AvailabilityMetrics Details:")
    print("=" * 80)
    
    metrics = AvailabilityMetrics.query.order_by(AvailabilityMetrics.id.desc()).limit(10).all()
    
    for metric in metrics:
        print(f"\nTram ID: {metric.tram_id}")
        print(f"  Report Period: {metric.report_period}")
        print(f"  Availability %: {metric.availability_percentage}")
        print(f"  Created At: {metric.created_at}")
        print(f"  Metric Date: {metric.metric_date}")
        print(f"  Operational Hours: {metric.operational_hours}")
        print(f"  Downtime Hours: {metric.downtime_hours}")
        print(f"  Failure Count: {metric.failure_count}")
