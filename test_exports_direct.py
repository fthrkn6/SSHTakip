"""
Test export endpoints to verify Excel files are created correctly
"""

from app import create_app
from utils_service_status import ExcelReportGenerator
import os

app = create_app()

# Test data
print("=" * 70)
print("TESTING EXCEL REPORT GENERATION")
print("=" * 70)

with app.app_context():
    output_dir = 'logs/rapor_cikti'
    os.makedirs(output_dir, exist_ok=True)
    
    # Import Equipment
    from models import Equipment
    
    # Test 1: Comprehensive Report
    print("\n[TEST 1] Creating Comprehensive Report...")
    try:
        tram_ids = [eq.equipment_code for eq in Equipment.query.all()]
        filepath = os.path.join(output_dir, 'TEST_Comprehensive.xlsx')
        ExcelReportGenerator.create_comprehensive_availability_report(tram_ids, filepath)
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"✓ SUCCESS: File created ({file_size} bytes)")
            print(f"  Location: {filepath}")
        else:
            print("✗ FAILED: File not created")
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Root Cause Report
    print("\n[TEST 2] Creating Root Cause Report...")
    try:
        tram_ids = [eq.equipment_code for eq in Equipment.query.all()]
        filepath = os.path.join(output_dir, 'TEST_RootCause.xlsx')
        ExcelReportGenerator.create_root_cause_analysis_report(tram_ids, filepath)
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"✓ SUCCESS: File created ({file_size} bytes)")
            print(f"  Location: {filepath}")
        else:
            print("✗ FAILED: File not created")
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Daily Report
    print("\n[TEST 3] Creating Daily Report...")
    try:
        first_equipment = Equipment.query.first()
        if first_equipment:
            filepath = os.path.join(output_dir, 'TEST_Daily.xlsx')
            ExcelReportGenerator.create_detailed_daily_report(first_equipment.equipment_code, filepath)
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"✓ SUCCESS: File created ({file_size} bytes)")
                print(f"  Location: {filepath}")
            else:
                print("✗ FAILED: File not created")
        else:
            print("✗ No equipment found")
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
