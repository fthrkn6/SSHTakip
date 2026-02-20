#!/usr/bin/env python3
"""Debug script to test FRACAS page rendering"""

from app import create_app
from models import db, User
import json

# Create Flask app instance
app = create_app()

# Create test user 
with app.app_context():
    # Check if test user exists
    test_user = User.query.filter_by(username='testuser').first()
    if not test_user:
        # Create test user
        test_user = User(username='testuser', email='test@test.com', role='admin')
        test_user.set_password('password')
        db.session.add(test_user)
        db.session.commit()
        print("Test user created")
    
    # Test with Flask test client - disable CSRF for testing
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        # First get the login page to get session
        client.get('/')
        
        # Post login request
        resp = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password'
        }, follow_redirects=True)
        
        print(f"Login response: {resp.status_code}")
        
        # Now get FRACAS page
        response = client.get('/fracas/')
        
        print(f"FRACAS Response Status: {response.status_code}")
        print("\n=== CHECKING FOR GRAPHICS DATA ===\n")
        
        # Check if pareto data is in the template context
        content = response.get_data(as_text=True)
        
        # Search for indicators of pareto data
        indicators = [
            'by_module',
            'by_supplier', 
            'paretoModuleChart',
            'paretoSupplierChart',
            'Pareto',
            'FRACAS Analiz',
            'data_available'
        ]
        
        for indicator in indicators:
            count = content.count(indicator)
            print(f"'{indicator}': found {count} times")
        
        # Check for error messages
        if 'İstatistik hesaplaması hatası' in content:
            print("\n[ERROR] Stats calculation error found in HTML!")
            # Try to extract error
            import re
            match = re.search(r"İstatistik hesaplaması hatası:.*?<", content, re.DOTALL)
            if match:
                print(f"Error message: {match.group(0)[:400]}")
        
        # Check if data_available is True or False
        if 'Excel Dosyası Bulunamadı' in content:
            print("\n[INFO] Page rendered with 'Excel Dosyası Bulunamadı' message")
        else:
            print("\n[INFO] Page seems to have data available")
        
        # Try to find page title
        if '<title>' in content:
            import re
            match = re.search(r'<title>(.*?)</title>', content)
            if match:
                print(f"\n[PAGE TITLE] {match.group(1)}")
        
        # Print first 2000 chars of body to see what's happening
        print("\n=== FIRST 2000 CHARS OF HTML ===")
        print(content[max(0, content.find('<body')):min(len(content), content.find('<body')+2000)])
