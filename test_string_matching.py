#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug işletme kaynaklı string matching"""

status_value = 'İşletme Kaynaklı Servis Dışı'

print(f"\nStatus: {status_value}")
print(f"Status lower: {status_value.lower()}")

# Test 1
if 'işletme kaynaklı' in status_value.lower():
    print("✅ Test 1: 'işletme kaynaklı' FOUND")
else:
    print("❌ Test 1: 'işletme kaynaklı' NOT FOUND")

# Test 2
if 'isletme' in status_value.lower():
    print("✅ Test 2: 'isletme' FOUND")
else:
    print("❌ Test 2: 'isletme' NOT FOUND")

# Test 3
if 'servis dişi' in status_value.lower():
    print("✅ Test 3: 'servis dişi' FOUND")
else:
    print("❌ Test 3: 'servis dişi' NOT FOUND")

# Test 4
if 'servis dışı' in status_value.lower():
    print("✅ Test 4: 'servis dışı' FOUND")
else:
    print("❌ Test 4: 'servis dışı' NOT FOUND")
