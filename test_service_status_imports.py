#!/usr/bin/env python3
"""
Test service status endpoint
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports
try:
    from routes.service_status import log_service_status
    print("✅ routes.service_status loaded")
except Exception as e:
    print(f"❌ Error importing routes.service_status: {e}")
    import traceback
    traceback.print_exc()

try:
    from utils_availability import AvailabilityCalculator, log_service_status_change
    print("✅ AvailabilityCalculator imported")
except Exception as e:
    print(f"❌ Error importing AvailabilityCalculator: {e}")
    import traceback
    traceback.print_exc()

try:
    from utils_excel_grid_manager import ExcelGridManager, RCAExcelManager
    print("✅ ExcelGridManager imported")
except Exception as e:
    print(f"❌ Error importing ExcelGridManager: {e}")

try:
    from utils_daily_service_logger import log_service_status as log_service_to_file
    print("✅ log_service_to_file imported")
except Exception as e:
    print(f"❌ Error importing log_service_to_file: {e}")

try:
    from utils_service_status_excel_logger import log_service_status_to_excel
    print("✅ log_service_status_to_excel imported")
except Exception as e:
    print(f"❌ Error importing log_service_status_to_excel: {e}")

print("\n✅ All imports successful!")
