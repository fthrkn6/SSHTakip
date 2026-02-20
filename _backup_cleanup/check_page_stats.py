#!/usr/bin/env python3
"""Check what stats are being passed to template vs endpoint"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import User

app = create_app()
with app.app_context():
    # Create/get admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        from werkzeug.security import generate_password_hash
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
    
    with app.test_client() as client:
        # Login
        client.post('/login', data={'username': 'admin', 'password': 'admin123'})
        
        # Get the page (this will show what stats are in template)
        page_response = client.get('/servis/durumu')
        print("\n" + "="*70)
        print("DOM CONTENT CHECK")
        print("="*70)
        
        page_content = page_response.get_data(as_text=True)
        
        # Extract stats from HTML
        import re
        
        # Find the stats values in the analytics cards
        patterns = [
            (r'<h3>Serviste</h3>.*?<div class="value"[^>]*>(\d+)', 'Serviste (Template)'),
            (r'<h3>Servis Dışı</h3>.*?<div class="value"[^>]*>(\d+)', 'Servis Dışı (Template)'),
            (r'<h3>İşletme</h3>.*?<div class="value"[^>]*>(\d+)', 'İşletme (Template)'),
            (r'<h3>Toplam Araç</h3>.*?<div class="value"[^>]*>(\d+)', 'Toplam (Template)'),
            (r'<div class="value" id="avgAvailability">([^<]+)', 'Availability (Template)'),
        ]
        
        for pattern, label in patterns:
            match = re.search(pattern, page_content, re.DOTALL)
            if match:
                print(f"{label}: {match.group(1)}")
            else:
                print(f"{label}: NOT FOUND")
        
        print("\n" + "="*70)
        print("ENDPOINT CHECK")
        print("="*70)
        
        # Get endpoint data
        endpoint_response = client.get('/servis/durumu/tablo')
        if endpoint_response.status_code == 200:
            data = endpoint_response.get_json()
            if 'stats' in data:
                print(f"Endpoint Stats:")
                for key, val in data['stats'].items():
                    print(f"  {key}: {val}")
        
        print("\n" + "="*70 + "\n")
