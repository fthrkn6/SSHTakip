#!/usr/bin/env python
"""Test to find which page returns 500 error"""

import requests
import time

# Wait for server
time.sleep(1)

base_url = "http://localhost:5000"

# Create a session to maintain cookies
session = requests.Session()

print("Testing various endpoints...\n")

endpoints = [
    "/",
    "/login",
    "/proje-sec",
]

for endpoint in endpoints:
    url = f"{base_url}{endpoint}"
    try:
        print(f"GET {endpoint:40}", end=" ", flush=True)
        response = session.get(url, timeout=5, allow_redirects=False)
        
        if response.status_code == 500:
            print(f"❌ 500 ERROR")
            print(f"Response:\n{response.text[:500]}")
        elif response.status_code in [301, 302, 303, 307, 308]:
            print(f"↪️  {response.status_code} -> {response.headers.get('Location', 'N/A')}")
        elif response.status_code == 200:
            print(f"✅ 200 OK")
        else:
            print(f"⚠️  {response.status_code}")
            
    except Exception as e:
        print(f"❌ {type(e).__name__}: {str(e)}")

# Try to login
print("\n\nTrying to login...")
login_data = {
    'username': 'admin',
    'password': 'admin123'
}

try:
    response = session.post(f"{base_url}/login", data=login_data, timeout=5)
    print(f"Login response: {response.status_code}")
    
    if response.status_code == 500:
        print(f"❌ 500 ERROR ON LOGIN")
        print(f"Response:\n{response.text[:1000]}")
        
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")

# Try dashboard
print("\n\nTrying dashboard...")
try:
    response = session.get(f"{base_url}/dashboard", timeout=5)
    print(f"Dashboard response: {response.status_code}")
    
    if response.status_code == 500:
        print(f"❌ 500 ERROR ON DASHBOARD")
        print(f"Response:\n{response.text[:1000]}")
        
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")
