#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test logging integration for ServiceStatus changes
"""
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from utils_service_status_logger import ServiceStatusLogger

def test_logging_integration():
    """Test all logging scenarios"""
    
    test_date = date.today().strftime('%Y-%m-%d')
    log_dir = Path('logs/service_status_history')
    
    print("=" * 60)
    print("🔍 SERVICE STATUS LOGGING INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: Single record logging
    print("\n1️⃣  Testing single record logging...")
    ServiceStatusLogger.log_status_change(
        tram_id='9001',
        date=test_date,
        status='Servis',
        sistem='Test Sistemi',
        alt_sistem='Test Alt Sistemi',
        aciklama='Test kaydı - Tek araç',
        user_id=99
    )
    print("   ✅ Single record logged")
    
    # Test 2: Multiple records (bulk operation)
    print("\n2️⃣  Testing bulk operation logging...")
    for i in range(3):
        ServiceStatusLogger.log_status_change(
            tram_id=f'900{2+i}',
            date=test_date,
            status='İşletme Kaynaklı Servis Dışı',
            sistem='',
            alt_sistem='',
            aciklama='Toplu servise alındı (test)',
            user_id=1
        )
    print("   ✅ Bulk records logged (3 records)")
    
    # Test 3: Different statuses
    print("\n3️⃣  Testing different status types...")
    statuses = ['Servis', 'Servis Dışı', 'İşletme Kaynaklı Servis Dışı']
    for i, status in enumerate(statuses):
        ServiceStatusLogger.log_status_change(
            tram_id=f'910{i}',
            date=test_date,
            status=status,
            sistem='Mixed Test',
            alt_sistem='',
            aciklama=f'Status test: {status}',
            user_id=2
        )
    print(f"   ✅ All {len(statuses)} status types logged")
    
    # Verify files were created
    print("\n📁 Verifying log files...")
    json_file = log_dir / f'service_status_log_{test_date}.json'
    excel_file = log_dir / f'service_status_log_{test_date}.xlsx'
    
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        print(f"   ✅ JSON log file exists with {len(json_data)} entries")
        
        # Show sample entries
        print("\n   📋 Sample entries from log:")
        for entry in json_data[-3:]:  # Last 3 entries
            print(f"      - {entry['timestamp']}: {entry['tram_id']} ({entry['status']})")
    else:
        print(f"   ❌ JSON log file not found: {json_file}")
        return False
    
    if excel_file.exists():
        print(f"   ✅ Excel log file exists: {excel_file.name}")
    else:
        print(f"   ❌ Excel log file not found: {excel_file}")
        return False
    
    # Test 4: Log retrieval
    print("\n4️⃣  Testing log retrieval...")
    try:
        all_logs = ServiceStatusLogger.get_all_logs(test_date, test_date)
        print(f"   ✅ Retrieved {len(all_logs)} logs for {test_date}")
        
        # Count by status
        status_counts = {}
        for log in all_logs:
            status = log.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("\n   📊 Log breakdown by status:")
        for status, count in status_counts.items():
            print(f"      - {status}: {count} entries")
    except Exception as e:
        print(f"   ❌ Error retrieving logs: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL LOGGING INTEGRATION TESTS PASSED!")
    print("=" * 60)
    print(f"\n📍 Log files location: {log_dir}")
    print(f"📅 Today's logs: service_status_log_{test_date}.json/xlsx")
    print("\n🎯 Integration Status: COMPLETE")
    print("   ✅ Single record logging")
    print("   ✅ Bulk operation logging")
    print("   ✅ Multiple status types")
    print("   ✅ File creation (JSON + Excel)")
    print("   ✅ Log retrieval")
    
    return True

if __name__ == '__main__':
    success = test_logging_integration()
    exit(0 if success else 1)
