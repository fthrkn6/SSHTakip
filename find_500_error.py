#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find which endpoint returns 500"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db, User
import traceback

app = create_app()

with app.app_context():
    client = app.test_client()
    
    # Create test user
    if not User.query.filter_by(username='admin').first():
        user = User(username='admin', email='admin@admin.com', role='admin')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
    
    # Login
    client.post('/login', data={
        'username': 'admin',
        'password': 'admin123',
        'project': 'belgrad'
    }, follow_redirects=True)
    
    # Test main endpoints
    endpoints = [
        '/dashboard/',
        '/api/bakim-verileri',
        '/tramvay-km',
        '/fracas',
    ]
    
    print("[Testing Endpoints for 500 errors]")
    for endpoint in endpoints:
        try:
            response = client.get(endpoint)
            symbol = '✓' if response.status_code < 400 else '✗'
            print(f"{symbol} {endpoint}: {response.status_code}")
            
            if response.status_code >= 400:
                # Get error details
                html = response.data.decode('utf-8', errors='ignore')
                
                # Look for Python traceback
                if 'Traceback' in html:
                    # Extract error message
                    start = html.find('Traceback')
                    end = html.find('</pre>', start)
                    if start > 0 and end > 0:
                        tb = html[start:end]
                        # Print just the last line (actual error)
                        lines = tb.split('\n')
                        error_line = [l for l in lines if l.strip()][-1] if lines else ''
                        print(f"    Error: {error_line[:150]}")
                elif '500' in html:
                    print(f"    500 error page returned")
        except Exception as e:
            print(f"✗ {endpoint}: Exception - {str(e)[:100]}")
            traceback.print_exc()
