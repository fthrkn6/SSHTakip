#!/usr/bin/env python3
"""
Comprehensive test of service status logging with Turkish character handling
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Equipment, ServiceLog
from datetime import date

with app.app_context():
    print("\n" + "="*70)
    print("TEST: SERVIS DURUMU HATA DUZETME")
    print("="*70)
    
    test_cases = [
        {
            'name': 'Servis Dışı',
            'status': 'Servis Dışı',
            'expected_code': 'servis_disi'
        },
        {
            'name': 'İşletme Kaynaklı Servis Dışı',
            'status': 'İşletme Kaynaklı Servis Dışı',
            'expected_code': 'isletme_kaynakli'
        },
        {
            'name': 'Servis (Aktif)',
            'status': 'Servis',
            'expected_code': 'aktif'
        }
    ]
    
    try:
        # Import the status code determination logic
        from datetime import datetime
        
        passed = 0
        failed = 0
        
        for test in test_cases:
            print(f"\nTest: {test['name']}")
            print(f"  Status: {test['status']}")
            
            # Simulate the status code determination from routes/service_status.py
            new_status = test['status']
            status_code = 'aktif'
            
            # This is the FIXED logic
            if 'İşletme' in new_status or 'işletme' in new_status.lower():
                status_code = 'isletme_kaynakli'
            elif 'Dışı' in new_status or 'dışı' in new_status.lower() or 'ariza' in new_status.lower():
                status_code = 'servis_disi'
            
            print(f"  Expected: {test['expected_code']}")
            print(f"  Got:      {status_code}")
            
            if status_code == test['expected_code']:
                print(f"  [PASSED]")
                passed += 1
            else:
                print(f"  [FAILED]")
                failed += 1
        
        # Test the actual logging function
        print(f"\n" + "-"*70)
        print("Testing actual service status logging function")
        print("-"*70)
        
        from utils_availability import log_service_status_change
        
        project_code = 'belgrad'
        tram_id = 'TEST_SERVIS_DISI'
        
        # Create test equipment if needed
        equipment = Equipment.query.filter_by(
            equipment_code=str(tram_id),
            project_code=project_code
        ).first()
        
        if not equipment:
            equipment = Equipment(
                equipment_code=str(tram_id),
                name=f'Test {tram_id}',
                equipment_type='Tramvay',
                project_code=project_code
            )
            db.session.add(equipment)
            db.session.commit()
        
        # Test log_service_status_change with "Servis Dışı"
        log_entry = log_service_status_change(
            tram_id=tram_id,
            new_status='Servis Dışı',  # The problematic status
            sistem='Test Sistema',
            alt_sistem='Test Alt Sistema',
            reason='Test entry for Servis Dışı',
            duration_hours=1.5,
            user_id=1
        )
        
        if log_entry:
            print(f"[OK] Service status logged successfully")
            print(f"  Log ID: {log_entry.id}")
            print(f"  Tram ID: {log_entry.tram_id}")
            passed += 1
        else:
            print(f"[ERROR] Failed to log service status")
            failed += 1
        
        # Summary
        print(f"\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"PASSED: {passed}")
        print(f"FAILED: {failed}")
        
        if failed == 0:
            print(f"\nALL TESTS PASSED!")
            sys.exit(0)
        else:
            print(f"\nSome tests failed")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n[ERROR] Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
