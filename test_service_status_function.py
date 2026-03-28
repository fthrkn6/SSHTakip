#!/usr/bin/env python3
"""
Test service status logging function directly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Flask app context
from app import app, db
from models import ServiceStatus, Equipment
from datetime import date

with app.app_context():
    try:
        # Test the imports that the endpoint uses
        from routes.service_status import log_service_status
        from utils_availability import log_service_status_change, AvailabilityCalculator
        from utils_excel_grid_manager import ExcelGridManager
        
        print("✅ All imports successful")
        
        # Create test data
        project_code = 'belgrad'
        tram_id = 'G1001'
        
        # Check if equipment exists
        equipment = Equipment.query.filter_by(
            equipment_code=str(tram_id), 
            project_code=project_code
        ).first()
        
        if equipment:
            print(f"✅ Equipment found: {equipment.name}")
        else:
            print(f"⚠️ Equipment not found for {tram_id}, creating test...")
            equipment = Equipment(
                equipment_code=str(tram_id),
                name=f'Test Tramvay {tram_id}',
                equipment_type='Tramvay',
                project_code=project_code
            )
            db.session.add(equipment)
            db.session.commit()
            print(f"✅ Equipment created: {equipment.name}")
        
        # Test log_service_status_change function
        print("\n🔍 Testing log_service_status_change...")
        try:
            log_entry = log_service_status_change(
                tram_id=tram_id,
                new_status='Servis Dışı',
                sistem='Lastik Sistem',
                alt_sistem='Tekerlek',
                reason='Test error',
                duration_hours=2,
                user_id=1
            )
            print(f"✅ log_service_status_change succeeded: {log_entry}")
        except Exception as e:
            print(f"❌ log_service_status_change failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test AvailabilityCalculator
        print("\n🔍 Testing AvailabilityCalculator...")
        try:
            result = AvailabilityCalculator.calculate_daily_availability(tram_id)
            print(f"✅ AvailabilityCalculator.calculate_daily_availability succeeded: {result}")
        except Exception as e:
            print(f"❌ AvailabilityCalculator.calculate_daily_availability failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test ExcelGridManager
        print("\n🔍 Testing ExcelGridManager...")
        try:
            grid_manager = ExcelGridManager(project_code)
            print(f"✅ ExcelGridManager created")
            
            availability_data = grid_manager.get_availability_data(app.root_path)
            print(f"✅ ExcelGridManager.get_availability_data succeeded: {len(availability_data)} records")
        except Exception as e:
            print(f"❌ ExcelGridManager failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
