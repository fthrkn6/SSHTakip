#!/usr/bin/env python3
"""Test the /servis/durumu/tablo endpoint response"""
import sys
import json
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment, ServiceStatus
from datetime import date

app = create_app()
with app.app_context():
    with app.test_client() as client:
        # Change session to belgrad
        with client.session_transaction() as session:
            session['current_project'] = 'belgrad'
        
        # Make request to endpoint
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
                print(f"\nStats (from endpoint):")
                for key, val in data['stats'].items():
                    print(f"  {key}: {val}")
            
            if 'table_data' in data:
                print(f"\nTable Data Count: {len(data['table_data'])}")
                if data['table_data']:
                    print(f"First Record Sample:")
                    print(f"  {data['table_data'][0]}")
            else:
                print(f"\nDirect Array Data Count: {len(data)}")
                if data:
                    print(f"First Record Sample:")
                    print(f"  {data[0]}")
        else:
            print(f"\nError Response: {response.get_data(as_text=True)}")
        
        print("\n" + "="*70 + "\n")
