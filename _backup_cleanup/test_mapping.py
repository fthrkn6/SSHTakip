#!/usr/bin/env python3
"""Test the exact mapping logic"""

test_values = [
    "Servis",
    "Servis Dışı", 
    "İşletme Kaynaklı Servis Dışı"
]

for test in test_values:
    status_value = test.lower()
    print(f"\nTesting: '{test}' -> lower: '{status_value}'")
    
    if 'işletme kaynaklı' in status_value:
        result = 'isletme'
        print(f"  ✓ Matched 'işletme kaynaklı' -> {result}")
    elif 'servis dışı' in status_value:
        result = 'ariza'
        print(f"  ✓ Matched 'servis dışı' -> {result}")
    elif 'servis' in status_value:
        result = 'aktif'
        print(f"  ✓ Matched 'servis' -> {result}")
    else:
        result = 'aktif'
        print(f"  ✓ Default -> {result}")
