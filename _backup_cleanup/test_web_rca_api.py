#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Web API test - RCA raporunu çağır"""
import sys
from datetime import datetime
sys.path.insert(0, '.')

client = None

def test_web_rca():
    from app import create_app, db
    from models import User
    
    app = create_app()
    
    # Test kullanıcı oluştur
    with app.app_context():
        # Test user - varsa kullan, yoksa oluştur
        user = User.query.filter_by(username='test_rca').first()
        if not user:
            user = User(username='test_rca', email='test_rca@test.com')
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()
        
        # Client oluştur
        client = app.test_client()
        
        # Login yap
        resp = client.post('/giris', data={
            'username': 'test_rca',
            'password': 'test123'
        }, follow_redirects=True)
        print(f"Login: {resp.status_code}")
        
        # RCA API'yi ara
        print("\n1. Default parametrelerle:")
        resp = client.get('/servis-durumu/root-cause-analysis', follow_redirects=False)
        print(f"   Status: {resp.status_code}")
        if resp.status_code in [301, 302, 303, 307, 308]:
            print(f"   Redirect: {resp.headers.get('Location')}")
        else:
            print(f"   Content-Type: {resp.headers.get('Content-Type')}")
            print(f"   Size: {len(resp.data)} bytes")
        
        if resp.status_code == 200:
            print(f"   Başlık: {resp.data[:100]}")
        
        # Parametrelerle
        print("\n2. Parametrelerle:")
        resp = client.get('/servis-durumu/root-cause-analysis?start_date=2026-02-01&end_date=2026-02-16', follow_redirects=False)
        print(f"   Status: {resp.status_code}")
        if resp.status_code in [301, 302, 303, 307, 308]:
            print(f"   Redirect: {resp.headers.get('Location')}")
        else:
            print(f"   Content-Type: {resp.headers.get('Content-Type')}")
            print(f"   Size: {len(resp.data)} bytes")

if __name__ == '__main__':
    test_web_rca()
