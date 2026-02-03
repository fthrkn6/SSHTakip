#!/usr/bin/env python
"""Direct test of /arizalar route"""

import os
import sys
sys.path.insert(0, os.getcwd())

from create_app import create_app
from flask_login import FlaskLoginUser

# Create app
app = create_app()

# Mock user
class MockUser:
    def is_authenticated(self):
        return True
    is_authenticated = True

# Test route directly
with app.test_client() as client:
    with app.test_request_context():
        # Try to access /arizalar
        response = client.get('/arizalar')
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 302:
            print(f"Redirected to: {response.location}")
            print(f"Need to login first")
        else:
            print(f"Response length: {len(response.data)}")
            if b'BEL25' in response.data:
                print(f"✓ Data found in response!")
            else:
                print(f"✗ Data not found in response")
