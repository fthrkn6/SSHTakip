#!/usr/bin/env python
"""Test script to identify which route causes 500 error"""

import requests
import time
import json

# Wait for server to start
time.sleep(2)

print("=" * 80)
print("TESTING ROUTES FOR 500 ERRORS")
print("=" * 80)

base_url = "http://localhost:5000"

# Test routes (these should be accessible without auth or redirect properly)
test_routes = [
    "/",                          # Index/Home
    "/login",                     # Login page
    "/proje-sec",                 # Project selection
    "/dashboard/",                # Dashboard
    "/dashboard",                 # Dashboard (without slash)
    "/arizalar",                  # Failures list
    "/ariza-listesi",             # Alias
    "/is-emirleri",               # Work orders
    "/bakim-planlari",            # Maintenance plans
    "/yedek-parca",               # Spare parts
    "/ekipmanlar",                # Equipment
    "/tramvay-km",                # Tram KM
    "/servis-durumu",             # Service status
    "/ariza-listesi-veriler",     # Failure list data
]

for route in test_routes:
    try:
        url = f"{base_url}{route}"
        print(f"\n📍 Testing {route:30} ... ", end="", flush=True)
        
        response = requests.get(url, allow_redirects=True, timeout=5)
        
        if response.status_code == 500:
            print(f"❌ 500 ERROR")
            print(f"   URL: {response.url}")
            print(f"   Content length: {len(response.text)}")
            if "Internal Server Error" in response.text:
                print("   ⚠️  This route returns 500 error!")
        elif response.status_code == 302 or response.status_code == 308:
            print(f"⏭️  {response.status_code} Redirect")
        elif response.status_code == 200:
            print(f"✅ {response.status_code} OK")
        else:
            print(f"⚠️  {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"⏱️  TIMEOUT")
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR - Server may not be running")
        break
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
