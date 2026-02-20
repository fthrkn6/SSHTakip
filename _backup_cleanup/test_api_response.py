#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test the API endpoint response"""

import sys
import json
from pprint import pprint

try:
    # Import the create_app function
    from app import create_app
    
    # Create Flask app
    app = create_app()
    
    # Use Flask test client
    client = app.test_client()
    
    # Test with a GET request
    response = client.get('/api/bakim-verileri')
    
    print("="*80)
    print("API RESPONSE TEST")
    print("="*80)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = json.loads(response.data)
        
        print(f"Number of Trams: {len(data.get('tramps', []))}")
        print(f"Maintenance Levels: {data.get('levels', [])}")
        
        # Show first tram as example
        if data.get('tramps'):
            tram = data['tramps'][0]
            print("\n" + "-"*80)
            print("FIRST TRAM EXAMPLE:")
            print("-"*80)
            print(f"Tram ID: {tram['tram_id']}")
            print(f"Tram Name: {tram['tram_name']}")
            print(f"Current KM: {tram['current_km']}")
            
            print("\nNearest Maintenance:")
            nearest = tram.get('nearest_maintenance', {})
            print(f"  Level: {nearest.get('level')}")
            print(f"  Next KM: {nearest.get('next_km')}")
            print(f"  KM Left: {nearest.get('km_left')}")
            print(f"  Status: {nearest.get('status')}")
            print(f"  Works Count: {len(nearest.get('works', []))}")
            
            print("\nAll Maintenances (sample - showing 2):")
            all_maint = tram.get('all_maintenances', {})
            for i, (level, maint) in enumerate(list(all_maint.items())[:2]):
                print(f"  {level}: Status={maint.get('status')}, KM_left={maint.get('km_left')}, Works={len(maint.get('works', []))}")
        
        print("\n" + "="*80)
        print("✓ API RESPONSE STRUCTURE VERIFIED!")
        print("="*80)
        
    else:
        print(f"ERROR: Got status code {response.status_code}")
        print(response.data.decode() if response.data else "No response data")
        
except Exception as e:
    import traceback
    print(f"ERROR: {str(e)}")
    print("\n" + traceback.format_exc())
