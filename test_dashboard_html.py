#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test dashboard response in detail"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    client = app.test_client()
    
    # Create test user
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
    
    # Test dashboard with full HTML
    print("[Getting /dashboard/ response]")
    response = client.get('/dashboard/')
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content length: {len(response.data)}")
    
    # Check if response is HTML or error
    html_content = response.data.decode('utf-8', errors='ignore')
    
    if response.status_code == 500:
        print(f"\n[ERROR FOUND]")
        print(html_content[:2000])
    elif '500' in html_content or 'error' in html_content.lower():
        print(f"\n[ERROR IN HTML]")
        print(html_content[:2000])
    else:
        # Check for specific content
        if 'DOCTYPE' in html_content:
            print("[✓] Valid HTML found")
            print(f"First 500 chars: {html_content[:500]}")
        else:
            print("[✗] No HTML found")
            print(f"Content: {html_content[:500]}")
