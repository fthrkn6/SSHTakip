#!/usr/bin/env python
"""Test /arizalar endpoint with Flask test client"""

import os
import sys

sys.path.insert(0, os.getcwd())

from app import create_app
from models import db, User

# Create Flask app
app = create_app()

# Create test client
client = app.test_client()

with app.app_context():
    # Create test user
    user = User.query.filter_by(username='admin').first()
    if not user:
        user = User(username='admin', email='admin@test.com')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        print("✓ Test user created")
    
    # Login
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    
    print(f"Login response: {response.status_code}")
    
    # Access /arizalar
    print("\n" + "="*80)
    print("Accessing /arizalar...")
    print("="*80)
    
    response = client.get('/arizalar')
    
    print(f"Response status: {response.status_code}")
    print(f"Response length: {len(response.data)} bytes")
    
    # Check if data is in response
    if b'BEL25-001' in response.data:
        print("✓ Found BEL25-001 in response!")
    if b'BEL25-002' in response.data:
        print("✓ Found BEL25-002 in response!")
    if b'BEL25-003' in response.data:
        print("✓ Found BEL25-003 in response!")
    
    # Show first 2000 chars
    if response.status_code == 200:
        print("\nFirst 2000 characters of response:")
        print(response.data.decode('utf-8')[:2000])
