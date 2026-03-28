#!/usr/bin/env python3
"""
Quick test of KM Excel Logger functionality
"""

import os
import sys
from utils_km_excel_logger import KMExcelLogger

def test_km_excel_logger():
    """Test KM Excel logger functionality"""
    
    test_project = 'belgrad'
    
    print(f"\n{'='*60}")
    print("KM Excel Logger Test")
    print(f"{'='*60}\n")
    
    try:
        # Test 1: Create logger and verify file creation
        print("1️⃣  Creating KM Excel Logger for project: belgrad")
        logger = KMExcelLogger(test_project)
        print(f"   ✅ Logger created")
        print(f"   📁 Excel path: {logger.excel_path}")
        
        # Test 2: Add a sample KM entry
        print("\n2️⃣  Logging sample KM entry...")
        result = logger.log_km_to_excel(
            tram_id='G1001',
            previous_km=125000,
            new_km=125500,
            reason='Gün sonu sayımı',
            user='test_user',
            system_type='Manuel'
        )
        
        if result:
            print(f"   ✅ KM entry logged successfully")
        else:
            print(f"   ❌ Failed to log KM entry")
            return False
        
        # Test 3: Add another entry with different values
        print("\n3️⃣  Adding second KM entry...")
        result = logger.log_km_to_excel(
            tram_id='G1002',
            previous_km=98500,
            new_km=99000,
            reason='Sürü sonu kontrollü güncelleme',
            user='mert.yilmaz',
            system_type='Manuel'
        )
        
        if result:
            print(f"   ✅ Second entry logged")
        else:
            print(f"   ❌ Failed to log second entry")
            return False
        
        # Test 4: Verify file exists
        print("\n4️⃣  Verifying Excel file existence...")
        if os.path.exists(logger.excel_path):
            file_size = os.path.getsize(logger.excel_path)
            print(f"   ✅ Excel file exists")
            print(f"   📊 File size: {file_size} bytes")
        else:
            print(f"   ❌ Excel file not found at {logger.excel_path}")
            return False
        
        # Test 5: Get statistics
        print("\n5️⃣  Getting Excel statistics...")
        stats = logger.get_excel_stats()
        if stats:
            print(f"   ✅ Statistics retrieved")
            print(f"      - Record count: {stats['record_count']}")
            print(f"      - First date: {stats['first_date']}")
            print(f"      - Last date: {stats['last_date']}")
            print(f"      - Min KM: {stats['min_km']}")
            print(f"      - Max KM: {stats['max_km']}")
        else:
            print(f"   ❌ Failed to get statistics")
            return False
        
        # Test 6: Test with different project
        print("\n6️⃣  Testing with different project (kayseri)...")
        logger2 = KMExcelLogger('kayseri')
        result = logger2.log_km_to_excel(
            tram_id='T2001',
            previous_km=50000,
            new_km=50750,
            reason='Test entry for Kayseri',
            user='test_user',
            system_type='Otomatik'
        )
        
        if result and os.path.exists(logger2.excel_path):
            print(f"   ✅ Multi-project support working")
            print(f"   📁 Kayseri Excel: {logger2.excel_path}")
        else:
            print(f"   ❌ Multi-project support failed")
            return False
        
        print(f"\n{'='*60}")
        print("✅ ALL TESTS PASSED!")
        print(f"{'='*60}\n")
        
        # Show file locations
        print("📂 Excel files created:")
        logs_dir = 'logs/km'
        if os.path.exists(logs_dir):
            for file in os.listdir(logs_dir):
                filepath = os.path.join(logs_dir, file)
                size = os.path.getsize(filepath)
                print(f"   - {file} ({size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_km_excel_logger()
    sys.exit(0 if success else 1)
