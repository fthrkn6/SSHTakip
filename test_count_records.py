#!/usr/bin/env python
"""Test /arizalar with all records"""

import os
import sys
sys.path.insert(0, os.getcwd())

from app import create_app
from models import db, User

app = create_app()
client = app.test_client()

with app.app_context():
    # Create/get test user
    user = User.query.filter_by(username='admin').first()
    if not user:
        user = User(username='admin', email='admin@test.com')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
    
    # Login
    client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    
    # Access /arizalar
    response = client.get('/arizalar')
    
    print(f"Status: {response.status_code}")
    
    # Count FRACAS IDs - all types
    import re
    html = response.data.decode('utf-8')
    
    # Count BEL25- and BOZ- occurrences
    bel25_count = len(re.findall(r'BEL25-\d+', html))
    boz_count = len(re.findall(r'BOZ-BEL25-[A-Z]{2}-\d+', html))
    other_count = len(re.findall(r'(?:BEL|BOZ)\d+-[A-Z]{2}-\d+', html))
    
    print(f"BEL25 records: {bel25_count}")
    print(f"BOZ-BEL25 records: {boz_count}")
    print(f"Other records: {other_count}")
    
    # Extract all FRACAS IDs with better regex
    all_ids = re.findall(r'[A-Z]+-[A-Z0-9]*-\d+', html)
    print(f"\nTotal unique FRACAS IDs: {len(set(all_ids))}")
    print(f"Sample IDs: {sorted(set(all_ids))[:10]}")
