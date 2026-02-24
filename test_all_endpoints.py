#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test all endpoints to find which ones return 500"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db, User
import json

app = create_app()

with app.app_context():
    client = app.test_client()
    
    # Create test user if needed
    if not User.query.filter_by(username='test').first():
        user = User(username='test', email='test@test.com', role='admin')
        user.set_password('test')
        db.session.add(user)
        db.session.commit()
    
    # Login
    response = client.post('/login', data={
        'username': 'test',
        'password': 'test',
        'project': 'belgrad'
    }, follow_redirects=True)
    
    print(f"✓ Login: {response.status_code}")
    
    # Test various endpoints that might be called from dashboard
    endpoints = [
        '/dashboard/',
        '/dashboard/api/equipment-status',
        '/dashboard/api/work-order-trend',
        '/dashboard/api/failures',
        '/api/bakim-verileri',
        '/tramvay-km',
        '/bakim-planlari',
        '/fracas',
    ]
    
    print("\n[Testing Endpoints]")
    for endpoint in endpoints:
        try:
            response = client.get(endpoint)
            status_emoji = '✓' if response.status_code < 400 else '✗'
            print(f"{status_emoji} {endpoint}: {response.status_code}")
            
            if response.status_code >= 400:
                # Print first 500 chars of error
                error_text = response.data.decode('utf-8', errors='ignore')[:500]
                print(f"  Error: {error_text}")
        except Exception as e:
            print(f"✗ {endpoint}: Exception - {e}")
    
    print("\n[Testing API Endpoints with different methods]")
    api_endpoints = [
        ('/dashboard/api/failures', 'GET'),
        ('/dashboard/api/failures/1531', 'GET'),
        ('/dashboard/api/equipment-status', 'GET'),
    ]
    
    for endpoint, method in api_endpoints:
        try:
            if method == 'GET':
                response = client.get(endpoint)
            status_emoji = '✓' if response.status_code < 400 else '✗'
            print(f"{status_emoji} {endpoint} ({method}): {response.status_code}")
            
            if response.status_code >= 400:
                error_text = response.data.decode('utf-8', errors='ignore')[:500]
                print(f"  Error: {error_text}")
        except Exception as e:
            print(f"✗ {endpoint}: Exception - {e}")
