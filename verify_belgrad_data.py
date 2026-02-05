from models import db, Equipment, ServiceLog, RootCauseAnalysis, AvailabilityMetrics
from app import create_app

app = create_app()
with app.app_context():
    print("BELGRAD DATA CHECK")
    print("-" * 60)
    
    eq_count = Equipment.query.count()
    log_count = ServiceLog.query.count()
    rca_count = RootCauseAnalysis.query.count()
    metrics_count = AvailabilityMetrics.query.count()
    
    print(f"Equipment: {eq_count}")
    print(f"ServiceLog: {log_count}")
    print(f"RootCauseAnalysis: {rca_count}")
    print(f"AvailabilityMetrics: {metrics_count}")
    
    print("\nSample for 1531:")
    logs = ServiceLog.query.filter_by(tram_id='1531').count()
    rca = RootCauseAnalysis.query.filter_by(tram_id='1531').count()
    metrics = AvailabilityMetrics.query.filter_by(tram_id='1531').count()
    print(f"  Logs: {logs}, RCA: {rca}, Metrics: {metrics}")
