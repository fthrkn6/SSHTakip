#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick test for FracasWriter with app.root_path simulation"""

import os
import sys

# Workspace root'u al
workspace_root = os.path.dirname(os.path.abspath(__file__))

print(f"Workspace: {workspace_root}")
print()

from utils_fracas_writer import FracasWriter

# Test 1: base_path olmadan (default)
print("TEST 1: Default path resolution")
writer1 = FracasWriter()
print(f"  File path: {writer1.file_path}")
print(f"  Exists: {os.path.exists(writer1.file_path)}")
print()

# Test 2: base_path ile (Flask app root path gibi)
print("TEST 2: With base_path (Flask app.root_path)")
writer2 = FracasWriter(base_path=workspace_root)
print(f"  File path: {writer2.file_path}")
print(f"  Exists: {os.path.exists(writer2.file_path)}")
print()

# Test 3: Sample form data ile write
if os.path.exists(writer2.file_path):
    print("TEST 3: Writing sample data")
    sample_data = {
        'arac_numarasi': 'T99_TEST',
        'sistem': 'OKS',
        'alt_sistem': 'Sistem',
        'tedarikci': 'Test',
        'ariza_tanimi': 'Test ariza',
        'ariza_sinifi': 'Test',
        'hata_tarih': '2026-02-17',
        'hata_saat': '16:30',
        'ariza_tespit_yontemi': 'Bozankaya',
    }
    
    try:
        result = writer2.write_failure_data(sample_data)
        if result.get('success'):
            print(f"  SUCCESS! Row: {result['row']}, ID: {result['fracas_id']}")
        else:
            print(f"  FAILED: {result}")
    except Exception as e:
        import traceback
        print(f"  ERROR: {e}")
        print(f"  Trace:\n{traceback.format_exc()}")
else:
    print(f"ERROR: File not found: {writer2.file_path}")

print("\nDone!")
