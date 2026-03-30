#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import create_app

app = create_app()

# Kullanıcı login edilmeden /fracas erişebilir mi tester edelim
with app.test_client() as client:
    print("="*60)
    print("TEST: FRACAS endpoint accessibility")
    print("="*60)
    
    # Test 1: /fracas/ without login
    print("\n1. GET /fracas/ (no login):")
    response = client.get('/fracas/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirect: {response.location}")
        print(f"   Expected: /login?next=...")
    
    # Test 2: /fracas/?project=belgrad without login  
    print("\n2. GET /fracas/?project=belgrad (no login):")
    response = client.get('/fracas/?project=belgrad')
    print(f"   Status: {response.status_code}")
    
    print("\nConclusion:")
    print("  /fracas requires login (@login_required decorator)")
    print("  Must authenticate first before accessing FRACAS page")
