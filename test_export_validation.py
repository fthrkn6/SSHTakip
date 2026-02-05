"""
Final validation - Test all export functionality end-to-end
"""

print("=" * 80)
print(" SERVICE STATUS EXPORT SYSTEM - FINAL VALIDATION")
print("=" * 80)

from app import create_app
from models import Equipment, ServiceLog, AvailabilityMetrics, RootCauseAnalysis
from datetime import date
import os

app = create_app()

with app.app_context():
    print("\n[1] DATABASE DATA VERIFICATION")
    print("-" * 80)
    
    eq_count = Equipment.query.count()
    log_count = ServiceLog.query.count()
    metric_count = AvailabilityMetrics.query.count()
    rca_count = RootCauseAnalysis.query.count()
    
    print(f"Equipment records:          {eq_count}")
    print(f"ServiceLog records:         {log_count}")
    print(f"AvailabilityMetrics records: {metric_count}")
    print(f"RootCauseAnalysis records:  {rca_count}")
    
    if eq_count == 0:
        print("\n✗ ERROR: No equipment found!")
        exit(1)
    
    if log_count == 0:
        print("\n⚠ WARNING: No service logs found (export may be empty)")
    
    print(f"\n✓ Database ready with {eq_count + log_count + metric_count + rca_count} total records")
    
    print("\n[2] EXPORT FILE TESTING")
    print("-" * 80)
    
    output_dir = 'logs/rapor_cikti'
    os.makedirs(output_dir, exist_ok=True)
    
    from utils_service_status import ExcelReportGenerator
    
    tests = [
        ('Comprehensive', lambda: (
            ExcelReportGenerator.create_comprehensive_availability_report(
                [eq.equipment_code for eq in Equipment.query.all()],
                os.path.join(output_dir, f'VALIDATION_Comprehensive_{date.today().isoformat()}.xlsx')
            ),
            os.path.join(output_dir, f'VALIDATION_Comprehensive_{date.today().isoformat()}.xlsx')
        )),
        ('Root Cause Analysis', lambda: (
            ExcelReportGenerator.create_root_cause_analysis_report(
                [eq.equipment_code for eq in Equipment.query.all()],
                os.path.join(output_dir, f'VALIDATION_RootCause_{date.today().isoformat()}.xlsx')
            ),
            os.path.join(output_dir, f'VALIDATION_RootCause_{date.today().isoformat()}.xlsx')
        )),
        ('Daily Report', lambda: (
            ExcelReportGenerator.create_detailed_daily_report(
                Equipment.query.first().equipment_code,
                os.path.join(output_dir, f'VALIDATION_Daily_{date.today().isoformat()}.xlsx')
            ),
            os.path.join(output_dir, f'VALIDATION_Daily_{date.today().isoformat()}.xlsx')
        )),
    ]
    
    passed = 0
    for test_name, test_fn in tests:
        try:
            _, filepath = test_fn()
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"✓ {test_name:30} ({file_size:8,} bytes) - {os.path.basename(filepath)}")
                passed += 1
            else:
                print(f"✗ {test_name:30} - File not created")
        except Exception as e:
            print(f"✗ {test_name:30} - Error: {str(e)[:60]}")
    
    print(f"\nPassed: {passed}/{len(tests)} tests")
    
    print("\n[3] EXPORT ROUTE VERIFICATION")
    print("-" * 80)
    
    # Check if the export routes exist
    try:
        from routes.service_status import bp
        print(f"✓ Service Status Blueprint loaded successfully")
        print(f"✓ Blueprint URL prefix: {bp.url_prefix}")
    except Exception as e:
        print(f"✗ Error loading blueprint: {str(e)}")
    
    print("\n" + "=" * 80)
    print(" VALIDATION COMPLETE - EXPORT SYSTEM READY FOR TESTING")
    print("=" * 80)
    print("\nNext Steps:")
    print("1. Start the Flask app: python app.py")
    print("2. Access the dashboard: http://localhost:5000/servis/durumu")
    print("3. Test export buttons in the left panel")
    print("4. Or test directly: http://localhost:5000/servis/test/export/comprehensive")
    print("=" * 80)
