#!/usr/bin/env python3
"""Test the /servis/durumu/tablo endpoint with login"""
import sys
import json
sys.path.insert(0, '.')

from app import create_app, db
from models import User

app = create_app()
with app.app_context():
    with app.test_client() as client:
        # Check/create admin user
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
            print("Created admin user")
        
        # Login
        login_response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        
        print(f"Login Response: {login_response.status_code}")
        
        # Now make request to endpoint
        response = client.get('/servis/durumu/tablo')
        print("\n" + "="*70)
        print("ENDPOINT TEST: /servis/durumu/tablo")
        print("="*70)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Content-Type: {response.content_type}")
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"\nResponse Keys: {list(data.keys())}")
            
            if 'stats' in data:
                print(f"\n✅ STATS (from endpoint):")
                for key, val in data['stats'].items():
                    print(f"   {key}: {val}")
            else:
                print(f"\n❌ NO 'stats' key in response!")
            
            if 'table_data' in data:
                print(f"\nTable Data Count: {len(data['table_data'])}")
                if data['table_data']:
                    print(f"First Record Sample:")
                    first = data['table_data'][0]
                    for key in ['tram_id', 'name', 'status', 'availability']:
                        print(f"   {key}: {first.get(key, 'N/A')}")
            else:
                print(f"\nDirect Array Data (old format) Count: {len(data)}")
        else:
            print(f"\nError Status: {response.status_code}")
            print(f"Error Response: {response.get_data(as_text=True)[:200]}")
        
        print("\n" + "="*70 + "\n")
