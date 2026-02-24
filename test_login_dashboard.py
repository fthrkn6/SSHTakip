#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test login and dashboard access"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db, User
import traceback

app = create_app()

with app.app_context():
    client = app.test_client()
    
    print("[1] Testing login with 'admin' user...")
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin123',
        'project': 'belgrad',
        'remember': 'on'
    }, follow_redirects=False)
    
    print(f"Login response: {response.status_code}")
    print(f"Location header: {response.headers.get('Location')}")
    
    # Follow redirect to dashboard
    print("\n[2] Following redirect to dashboard...")
    response = client.get(response.headers.get('Location', '/'))
    print(f"Redirect target status: {response.status_code}")
    
    # Now try accessing dashboard without following redirects
    print("\n[3] Direct dashboard access (no follow)...")
    try:
        response = client.get('/dashboard/')
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            html = response.data.decode('utf-8', errors='ignore')
            if 'Traceback' in html:
                print("[ERROR FOUND IN RESPONSE]")
                # Extract traceback
                start = html.find('Traceback')
                end = html.find('</pre>', start)
                if start > 0 and end > 0:
                    print(html[start:end+10])
            else:
                print(f"Response (first 1000 chars):\n{html[:1000]}")
    except Exception as e:
        print(f"Exception: {e}")
        traceback.print_exc()
