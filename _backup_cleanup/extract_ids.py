#!/usr/bin/env python
"""Extract first 500 chars of table from /arizalar response"""

import os
import sys
sys.path.insert(0, os.getcwd())

from app import create_app
from models import db, User

app = create_app()
client = app.test_client()

with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if not user:
        user = User(username='admin', email='admin@test.com')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
    
    client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    response = client.get('/arizalar')
    
    html = response.data.decode('utf-8')
    
    # Find table content
    import re
    
    # Search for FRACAS ID patterns in HTML
    lines = html.split('\n')
    
    print("="*80)
    print("Searching for FRACAS ID patterns in HTML...")
    print("="*80)
    
    fracas_pattern = re.compile(r'[A-Z]+-[A-Z0-9]+-\d+|[A-Z]+-\d+')
    
    count = 0
    found_ids = []
    
    for i, line in enumerate(lines):
        if 'BEL25' in line or 'BOZ' in line:
            print(f"\nLine {i}: {line[:150]}")
            matches = fracas_pattern.findall(line)
            if matches:
                print(f"  Found: {matches}")
                found_ids.extend(matches)
            count += 1
            if count >= 10:
                break
    
    print(f"\n\nTotal unique IDs found: {len(set(found_ids))}")
    print(f"Sample IDs: {sorted(set(found_ids))[:20]}")
