#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    # Create test database in memory
    db.create_all()
    
    # Create test user
    test_user = User(username='testuser', email='test@test.com')
    test_user.set_password('password')
    db.session.add(test_user)
    db.session.commit()
    
    with app.test_client() as client:
        print("="* 60)
        print("TEST: FRACAS WITH LOGIN")
        print("=" * 60)
        
        # 1. Login
        print("\n1. Logging in...")
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'password',
            'project': 'belgrad'
        }, follow_redirects=True)
        print(f"   Status: {response.status_code}")
        
        # 2. Access FRACAS page
        print("\n2. Accessing /fracas/...")
        response = client.get('/fracas/', follow_redirects=True)
        print(f"   Status: {response.status_code}")
        print(f"   Response size: {len(response.data)} bytes")
        
        # 3. Check content
        print("\n3. Content checks:")
        checks = [
            (b'paretoModuleChart', 'Chart: paretoModuleChart'),
            (b'new Chart', 'Chart.js init'),
            (b'filter_start_date', 'Filter form'),
            (b'RAMS', 'RAMS metrics'),
        ]
        
        for bytesearch, label in checks:
            exists = bytesearch in response.data
            symbol = '[OK]' if exists else '[FAIL]'
            print(f"   {symbol} {label}")

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)
