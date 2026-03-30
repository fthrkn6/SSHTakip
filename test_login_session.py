#!/usr/bin/env python
"""
Login test - Session doğru mu kuruluyorTest
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db, User, Role

app = create_app()

with app.test_client() as client:
    with app.app_context():
        db.create_all()
        
        # Test user oluştur
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            user_role = Role.query.filter_by(name='operator').first()
            if not user_role:
                user_role = Role(name='operator', description='Operator')
                db.session.add(user_role)
                db.session.commit()
            
            test_user = User(
                username='testuser',
                email='test@test.com',
                password_hash='testpass123'
            )
            test_user.roles.append(user_role)
            db.session.add(test_user)
            db.session.commit()
            print("[*] Test user oluşturuldu")
        else:
            print("[*] Test user var zaten")
        
        # Step 1: LOGIN
        print("\n=== STEP 1: LOGIN POST ===")
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        print(f"Status: {response.status_code}")
        print(f"Headers Location: {response.headers.get('Location', 'YOK')}")
        
        # Session'ı kontrol et
        with client.session_transaction() as sess:
            print(f"Session keys: {list(sess.keys())}")
            print(f"Session user_id: {sess.get('user_id', 'YOK')}")
        
        # Step 2: Redirect ekip, GET homepage
        print("\n=== STEP 2: GET homepage (follow_redirects) ===")
        response = client.get('/', follow_redirects=True)
        print(f"Status: {response.status_code}")
        if 'logged_in_user' not in response.data.decode('utf-8', errors='ignore'):
            print("⚠ Homepage'de login info bulunamadı")
        
        # Step 3: FRACAS page'e git
        print("\n=== STEP 3: GET /fracas/ ===")
        response = client.get('/fracas/', follow_redirects=True)
        print(f"Status: {response.status_code}")
        html = response.data.decode('utf-8', errors='ignore')
        
        if 'Giri' in html or 'login' in html.lower():
            print("✗ LOGIN SAYFASIna REDIRECT EDİLDİ!")
            print(f"Title: {html[html.find('<title>'):html.find('</title>')+8] if '<title>' in html else 'NOT FOUND'}")
        elif 'paretoModuleChart' in html or 'Pareto' in html:
            print("✓ FRACAS sayfası render edildi!")
        else:
            print("? Belirsiz sayfa")
            print(f"Response ilk 300 char: {html[:300]}")
