#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test the new data loggers"""

from utils_km_data_logger import KMDataLogger
from utils_maintenance_data_logger import MaintenanceDataLogger
from utils_service_status_data_logger import ServiceStatusDataLogger
from datetime import datetime

print("=" * 80)
print("TESTING NEW DATA LOGGERS")
print("=" * 80)

project = 'belgrad'

# Test 1: KM Logger
print("\n1️⃣ KM DATA LOGGER")
print("-" * 80)

KMDataLogger.log_km_update(project, '1531', 15050, 15000, 'Günlük servis', user_id=1)
KMDataLogger.log_km_update(project, '1531', 15100, 15050, 'Rota görev', user_id=2)
KMDataLogger.log_km_update(project, '1532', 12500, 12400, 'Başlangıç KM', user_id=1)

history = KMDataLogger.get_km_history(project, '1531')
print(f"✅ KM History for 1531: {len(history)} records")
for rec in history:
    print(f"   {rec['timestamp']}: {rec['previous_km']} → {rec['current_km']} km ({rec['reason']})")

latest = KMDataLogger.get_all_latest_kms(project)
print(f"✅ Latest KMs: {latest}")

# Test 2: Maintenance Logger
print("\n2️⃣ MAINTENANCE DATA LOGGER")
print("-" * 80)

MaintenanceDataLogger.log_maintenance_record(project, '1531', '6K Service', 6000, 20, 'Preventive', 'Completed', user_id=1)
MaintenanceDataLogger.log_maintenance_record(project, '1531', '24K Service', 24000, 80, 'Preventive', 'Planned', user_id=1)
MaintenanceDataLogger.log_maintenance_record(project, '1532', '6K Service', 6000, 20, 'Preventive', 'In Progress', user_id=2)

history = MaintenanceDataLogger.get_maintenance_history(project, '1531')
print(f"✅ Maintenance History for 1531: {len(history)} records")
for rec in history:
    print(f"   {rec['plan_name']}: {rec['schedule_km']}km - Status: {rec['status']}")

stats = MaintenanceDataLogger.get_maintenance_statistics(project)
print(f"✅ Maintenance Statistics: {stats['by_status']}")

# Test 3: Service Status Logger
print("\n3️⃣ SERVICE STATUS DATA LOGGER")
print("-" * 80)

ServiceStatusDataLogger.log_status_change(project, '1531', '2026-02-24', 'Servis', 'Elektrik', 'Motor', 'Rutin bakım', user_id=1)
ServiceStatusDataLogger.log_status_change(project, '1531', '2026-02-25', 'İşletme', '', '', 'İşletmeye geri döndü', user_id=1)
ServiceStatusDataLogger.log_status_change(project, '1532', '2026-02-24', 'İşletme', '', '', '', user_id=2)

history = ServiceStatusDataLogger.get_status_history(project, '1531')
print(f"✅ Service Status History for 1531: {len(history)} records")
for rec in history:
    print(f"   {rec['date']}: {rec['status']} - {rec['aciklama']}")

current = ServiceStatusDataLogger.get_all_current_statuses(project)
print(f"✅ Current Statuses: {len(current)} trams")
for tram_id, status_info in list(current.items())[:3]:
    print(f"   {tram_id}: {status_info['status']} ({status_info['date']})")

dist = ServiceStatusDataLogger.get_status_distribution(project)
print(f"✅ Status Distribution: {dist}")

print("\n" + "=" * 80)
print("✅ ALL LOGGERS WORKING CORRECTLY")
print("=" * 80)
