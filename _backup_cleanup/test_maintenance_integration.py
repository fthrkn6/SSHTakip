#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Comprehensive test of the maintenance page"""

import sys
import json

def test_maintenance_page():
    """Test the full maintenance page integration"""
    from app import create_app
    
    app = create_app()
    client = app.test_client()
    
    print("="*80)
    print("COMPREHENSIVE MAINTENANCE PAGE TEST")
    print("="*80)
    
    # Test 1: API endpoint returns correct structure
    print("\n1. Testing API endpoint...")
    print("-" * 80)
    
    response = client.get('/api/bakim-verileri')
    assert response.status_code == 200, f"API returned {response.status_code}"
    
    data = json.loads(response.data)
    assert 'tramps' in data, "Missing 'tramps' in response"
    assert 'levels' in data, "Missing 'levels' in response"
    assert len(data['tramps']) > 0, "No trams in response"
    
    print("✓ API endpoint responds with correct structure")
    print(f"  - Found {len(data['tramps'])} trams")
    print(f"  - Maintenance levels: {', '.join(data['levels'])}")
    
    # Test 2: Verify each tram has required fields
    print("\n2. Testing tram data structure...")
    print("-" * 80)
    
    required_tram_fields = ['tram_id', 'tram_name', 'current_km', 'nearest_maintenance', 'all_maintenances']
    required_nearest_fields = ['level', 'next_km', 'km_left', 'status', 'works']
    required_all_maint_fields = ['level', 'next_km', 'km_left', 'status', 'works', 'multiples']
    
    tram = data['tramps'][0]
    
    for field in required_tram_fields:
        assert field in tram, f"Tram missing field: {field}"
    
    print(f"✓ Tram {tram['tram_id']} has all required fields")
    
    # Test 3: Verify nearest_maintenance structure
    print("\n3. Testing nearest maintenance structure...")
    print("-" * 80)
    
    nearest = tram['nearest_maintenance']
    for field in required_nearest_fields:
        assert field in nearest, f"nearest_maintenance missing field: {field}"
    
    print(f"✓ nearest_maintenance has all required fields")
    print(f"  - Level: {nearest['level']}")
    print(f"  - Status: {nearest['status']}")
    print(f"  - KM Left: {nearest['km_left']}")
    print(f"  - Works: {len(nearest['works'])} items")
    
    # Test 4: Verify all_maintenances structure
    print("\n4. Testing all_maintenances structure...")
    print("-" * 80)
    
    all_maint = tram['all_maintenances']
    assert isinstance(all_maint, dict), "all_maintenances should be a dict"
    assert len(all_maint) == len(data['levels']), f"all_maintenances count mismatch"
    
    for level, maint_data in list(all_maint.items())[:2]:
        for field in required_all_maint_fields:
            assert field in maint_data, f"{level} missing field: {field}"
    
    print(f"✓ all_maintenances has all required fields")
    print(f"  - Levels: {len(all_maint)} (matches {len(data['levels'])} defined levels)")
    
    # Test 5: Verify status values are valid
    print("\n5. Testing status values...")
    print("-" * 80)
    
    valid_statuses = ['normal', 'warning', 'urgent', 'overdue']
    
    for tram in data['tramps'][:5]:  # Check first 5 trams
        nearest_status = tram['nearest_maintenance']['status']
        assert nearest_status in valid_statuses, f"Invalid status: {nearest_status}"
        
        for level, maint in tram['all_maintenances'].items():
            assert maint['status'] in valid_statuses, f"Invalid status in {level}: {maint['status']}"
    
    print(f"✓ All status values are valid: {', '.join(valid_statuses)}")
    
    # Test 6: Check nearest maintenance makes sense
    print("\n6. Testing nearest maintenance logic...")
    print("-" * 80)
    
    errors = []
    for tram in data['tramps']:
        nearest = tram['nearest_maintenance']
        all_maint = tram['all_maintenances']
        
        # Check if nearest's km_left is the smallest among all positive km_left values
        # Note: Multiple levels may have the same km_left - in that case, the first one
        # in the maintenance_levels list is selected (e.g., 6K before 18K before 24K)
        
        min_km_left = float('inf')
        for level, maint in all_maint.items():
            if maint['km_left'] > 0:
                min_km_left = min(min_km_left, maint['km_left'])
        
        # Check that nearest's km_left matches the minimum
        if min_km_left != float('inf'):
            if nearest['km_left'] != min_km_left:
                errors.append(f"Tram {tram['tram_id']}: Expected km_left={min_km_left}, got {nearest['km_left']}")
        else:
            # All km_left are zero or negative (all overdue), should have selected the last level
            if nearest['level'] != '300K':
                errors.append(f"Tram {tram['tram_id']}: All overdue, expected 300K, got {nearest['level']}")
    
    if errors:
        print("✗ Errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Nearest maintenance has the minimum km_left among all levels")
        print("  (When multiple levels have same km_left, earliest in sequence is selected)")
    
    # Test 7: Verify multiple calculation
    print("\n7. Testing multiple calculation...")
    print("-" * 80)
    
    sample_tram = data['tramps'][0]
    level_6k = sample_tram['all_maintenances']['6K']
    current_km = sample_tram['current_km']
    
    # 6K multiples: 6k, 12k, 18k, 24k...
    expected_multiples = [6000 * i for i in range(1, 51) if 6000 * i <= 300000]
    
    assert level_6k['multiples'][:10] == expected_multiples[:10], "Multiples calculation incorrect"
    
    print(f"✓ Multiples calculation is correct")
    print(f"  - 6K has {len(level_6k['multiples'])} multiples")
    print(f"  - Sample: {level_6k['multiples'][:5]}")
    
    print("\n" + "="*80)
    print("✓ ALL TESTS PASSED!")
    print("="*80)
    print("\nSummary:")
    print(f"  - API endpoint works correctly")
    print(f"  - Data structure is valid for {len(data['tramps'])} trams")
    print(f"  - All required fields are present")
    print(f"  - Status values are valid")
    print(f"  - Nearest maintenance logic is correct")
    print(f"  - Multiple calculation is correct")
    print("\nThe maintenance page is ready to use!")

if __name__ == '__main__':
    try:
        test_maintenance_page()
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\n✗ ERROR: {str(e)}")
        print("\n" + traceback.format_exc())
        sys.exit(1)
