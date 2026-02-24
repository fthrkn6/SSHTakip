#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug dashboard error"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Patch print untuk UTF-8
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app
from models import db, User
import traceback

# Create app
app = create_app()

# Create test user
with app.app_context():
    if not User.query.filter_by(username='test').first():
        user = User(username='test', email='test@test.com', role='admin')
        user.set_password('test')
        db.session.add(user)
        db.session.commit()
        print("[OK] Test user created")
    
    # Test route
    client = app.test_client()
    
    # Login
    print("\n[1] Testing login...")
    response = client.post('/login', data={
        'username': 'test',
        'password': 'test',
        'project': 'belgrad'
    }, follow_redirects=True)
    print(f"Login response: {response.status_code}")
    
    # Test dashboard
    print("\n[2] Testing dashboard...")
    try:
        response = client.get('/dashboard/')
        print(f"Dashboard response: {response.status_code}")
        
        if response.status_code != 200:
            print(f"\n[ERROR] Response data:")
            print(response.data.decode('utf-8', errors='ignore')[:2000])
    except Exception as e:
        print(f"[ERROR] Exception:")
        print(traceback.format_exc())
    
    # Test API
    print("\n[3] Testing /api/bakim-verileri...")
    try:
        response = client.get('/api/bakim-verileri')
        print(f"API response: {response.status_code}")
        
        if response.status_code != 200:
            print(f"\n[ERROR] Response:")
            print(response.data.decode('utf-8', errors='ignore')[:2000])
            print(f"\n[ERROR] Full response data:")
            print(response.get_json())
    except Exception as e:
        print(f"[ERROR] Exception:")
        print(traceback.format_exc())
