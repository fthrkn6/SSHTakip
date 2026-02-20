#!/usr/bin/env python
"""Direct test to identify the login error"""

import sys
import os

# Add the app directory to path
sys.path.insert(0, 'c:\\Users\\ferki\\Desktop\\bozankaya_ssh_takip')

from app import create_app
from models import db, User

print("=" * 80)
print("TESTING LOGIN FUNCTIONALITY")
print("=" * 80)

# Create app
app = create_app()

with app.app_context():
    # Check if admin user exists
    admin = User.query.filter_by(username='admin').first()
    print(f"\n1. Admin user exists: {admin is not None}")
    
    if admin:
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        
        # Test password check
        result = admin.check_password('admin123')
        print(f"\n2. Password check result: {result}")
        
        if not result:
            print("   ❌ Password does not match!")
    else:
        print("   ❌ Admin user not found!")
    
    # Try to simulate a login request
    print(f"\n3. Testing form submission with test client...")
    
    client = app.test_client()
    
    try:
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 500:
            print(f"   ❌ Got 500 error")
            print(f"   Response data: {response.get_data(as_text=True)[:500]}")
        elif response.status_code == 200:
            print(f"   ✅ Got 200 OK")
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
