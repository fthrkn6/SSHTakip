import requests
import json

# Samsun project'i için bakım datası iste
print("Testing Samsun project selection...\n")

# Test 1: /api/projects endpoint (no auth needed)
print("Testing /api/projects endpoint:")
try:
    response = requests.get('http://localhost:5000/api/projects')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        projects = response.json()
        print(f"Projects returned: {len(projects)}")
        for p in projects:
            print(f"  - {p['code']}: {p['name']}")
        # Check if samsun is included
        samsun_found = any(p['code'] == 'samsun' for p in projects)
        print(f"✓ Samsun found: {samsun_found}")
    else:
        print(f"Response text: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Check if Samsun exists in data folder
print("\n" + "="*50)
import os
samsun_path = 'data/samsun'
print(f"Samsun folder exists: {os.path.exists(samsun_path)}")
if os.path.exists(samsun_path):
    files = os.listdir(samsun_path)
    print(f"  Files in data/samsun: {files}")
    
    # Check Veriler.xlsx
    veriler_path = os.path.join(samsun_path, 'Veriler.xlsx')
    print(f"  Veriler.xlsx exists: {os.path.exists(veriler_path)}")
