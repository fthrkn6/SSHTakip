from models import db, Equipment, ServiceLog, RootCauseAnalysis, AvailabilityMetrics
from app import create_app

app = create_app()
with app.app_context():
    print("=" * 80)
    print("BELGRAD PROJECT - TRAMWAY DATA CHECK")
    print("=" * 80)
    
    # Check equipment with IDs 1531, 1532, 1533
    for tram_id in ['1531', '1532', '1533']:
        eq = Equipment.query.filter_by(equipment_code=tram_id).first()
        if eq:
            print(f"\n{tram_id} - {eq.name}:")
            
            # ServiceLog count
            logs = ServiceLog.query.filter_by(tram_id=tram_id).all()
            print(f"  ServiceLog records: {len(logs)}")
            if logs:
                print(f"    Date range: {logs[0].log_date} to {logs[-1].log_date}")
                print(f"    Sample systems: {set([l.sistem for l in logs if l.sistem])}")
            
            # RootCauseAnalysis count
            rca = RootCauseAnalysis.query.filter_by(tram_id=tram_id).all()
            print(f"  RootCauseAnalysis records: {len(rca)}")
            if rca:
                print(f"    Sample systems: {set([r.sistem for r in rca if r.sistem])}")
                print(f"    Sample subsystems: {set([r.alt_sistem for r in rca if r.alt_sistem])}")
            
            # AvailabilityMetrics
            metrics = AvailabilityMetrics.query.filter_by(tram_id=tram_id).all()
            print(f"  AvailabilityMetrics records: {len(metrics)}")
            if metrics:
                print(f"    Periods: {set([m.report_period for m in metrics])}")
        else:
            print(f"\n{tram_id} - NOT FOUND")
