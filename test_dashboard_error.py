#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test dashboard para ver el error exacto"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db, User

# Crear app
app = create_app()

with app.app_context():
    # Crear usuario test si no existe
    test_user = User.query.filter_by(username='admin').first()
    if not test_user:
        test_user = User(username='admin', email='admin@test.com', role='admin')
        test_user.set_password('admin')
        db.session.add(test_user)
        db.session.commit()
    
    # Test client
    client = app.test_client()
    
    # Login
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin',
        'project': 'belgrad'
    }, follow_redirects=True)
    
    print(f"Login status: {response.status_code}")
    
    # Try dashboard
    try:
        response = client.get('/dashboard')
        print(f"Dashboard status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.data[:1000]}")
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
