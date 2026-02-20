#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Frontend hatasini bulma testi"""

import sys
import os
sys.path.insert(0, 'c:\\Users\\ferki\\Desktop\\bozankaya_ssh_takip')
os.chdir('c:\\Users\\ferki\\Desktop\\bozankaya_ssh_takip')

from app import create_app

app = create_app()
client = app.test_client()

print("=" * 80)
print("HATA TESHISI - DASHBOARD VE LOGIN")
print("=" * 80)

# 1. GET /login
print("\n[1] GET /login")
try:
    r = client.get('/login')
    print(f"    Status: {r.status_code}")
except Exception as e:
    print(f"    Hata: {e}")

# 2. POST /login
print("\n[2] POST /login")
try:
    r = client.post('/login', data={'username': 'admin', 'password': 'admin123'})
    print(f"    Status: {r.status_code}")
    if r.status_code == 500:
        metin = r.get_data(as_text=True)[:300]
        print(f"    Metin: {metin}")
except Exception as e:
    print(f"    Hata: {type(e).__name__}: {str(e)}")

# 3. GET /dashboard/
print("\n[3] GET /dashboard/")
try:
    r = client.get('/dashboard/')
    print(f"    Status: {r.status_code}")
    if r.status_code == 500:
        metin = r.get_data(as_text=True)[:300]
        print(f"    Metin: {metin}")
except Exception as e:
    print(f"    Hata: {type(e).__name__}: {str(e)}")

print("\n" + "=" * 80)
