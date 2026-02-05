"""
Simple export test to debug the issue
"""

from app import create_app, db
from models import Equipment, ServiceLog, AvailabilityMetrics, RootCauseAnalysis
import os

app = create_app()

with app.app_context():
    print("=" * 60)
    print("EQUIPMENT DATA:")
    print("=" * 60)
    equipments = Equipment.query.limit(5).all()
    for eq in equipments:
        print(f"  equipment_code: {eq.equipment_code}, name: {eq.name}")
    
    print("\n" + "=" * 60)
    print("SERVICE LOG DATA:")
    print("=" * 60)
    logs = ServiceLog.query.limit(5).all()
    print(f"Total ServiceLog records: {ServiceLog.query.count()}")
    for log in logs:
        print(f"  tram_id: {log.tram_id}, log_date: {log.log_date}, status: {log.new_status}")
    
    print("\n" + "=" * 60)
    print("AVAILABILITY METRICS DATA:")
    print("=" * 60)
    metrics = AvailabilityMetrics.query.limit(5).all()
    print(f"Total AvailabilityMetrics records: {AvailabilityMetrics.query.count()}")
    for metric in metrics:
        print(f"  tram_id: {metric.tram_id}, date: {metric.metric_date}, period: {metric.report_period}, availability: {metric.availability_percentage}%")
    
    print("\n" + "=" * 60)
    print("ROOT CAUSE DATA:")
    print("=" * 60)
    rcas = RootCauseAnalysis.query.limit(5).all()
    print(f"Total RootCauseAnalysis records: {RootCauseAnalysis.query.count()}")
    for rca in rcas:
        print(f"  tram_id: {rca.tram_id}, sistem: {rca.sistem}, cause: {rca.root_cause}")
    
    print("\n" + "=" * 60)
    print("MISMATCH CHECK:")
    print("=" * 60)
    print(f"Equipment codes: {[eq.equipment_code for eq in equipments]}")
    print(f"ServiceLog tram_ids: {[log.tram_id for log in ServiceLog.query.all()]}")
    print(f"Availability tram_ids: {list(set([m.tram_id for m in AvailabilityMetrics.query.all()]))}")
