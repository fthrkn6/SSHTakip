#!/usr/bin/env python3
"""
Test service status endpoint with actual POST request
"""

import requests
import json
from datetime import date

# Get CSRF token first (simulate login)
session = requests.Session()

# Test the endpoint
test_data = {
    'tram_id': 'G1001',
    'status': 'Servis Dışı',
    'sistem': 'Lastik Sistem',
    'alt_sistem': 'Tekerlek',
    'reason': 'Test servis dışı',
    'duration_hours': 0
}

print("Testing /servis/durumu/log endpoint")
print("=" * 60)
print(f"Test data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
print("=" * 60)

try:
    # Try to POST to the endpoint
    # Note: This will fail with 401 (unauthorized) since we're not logged in
    # But we can see if the route exists
    response = requests.post(
        'http://localhost:5000/servis/durumu/log',
        json=test_data,
        timeout=5
    )
    
    print(f"\n📡 Response Status: {response.status_code}")
    print(f"📄 Response Body: {response.text[:500]}")
    
    if response.status_code == 401:
        print("\n✅ Endpoint exists (returned 401 Unauthorized - expected without login)")
    elif response.status_code == 400:
        result = response.json()
        if 'error' in result:
            print(f"❌ Validation error: {result['error']}")
        else:
            print(f"❌ Bad request error: {result}")
    elif response.status_code == 200 or response.status_code == 201:
        result = response.json()
        if 'success' in result and result['success']:
            print(f"✅ Service status logged successfully!")
            print(f"   Response: {result}")
        else:
            print(f"❌ Error: {result}")
    else:
        print(f"❓ Unexpected status code: {response.status_code}")
        
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
