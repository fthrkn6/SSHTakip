#!/usr/bin/env python3
"""Test rapor web - CSRF Token ile"""
import requests
import re

BASE_URL = "http://127.0.0.1:5000"

print("\n" + "="*70)
print("WEB RAPOR TESTI - CSRF Token ile")
print("="*70 + "\n")

with requests.Session() as session:
    # [1] Login
    print("[1] Login...")
    login_data = {
        'username': 'admin',
        'password': 'password1'
    }
    
    resp = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    print(f"    Status: {resp.status_code}")
    if 'logout' not in resp.text.lower():
        print("    ✗ Login başarısız")
        exit(1)
    print("    ✓ Login başarılı\n")
    
    # [2] Form sayfasını eriş - CSRF token'ı al
    print("[2] Form sayfasından CSRF token alınıyor...")
    resp = session.get(f"{BASE_URL}/reports/management")
    
    # Token'ı ara
    csrf_token = None
    pattern = r'csrf_token["\']?\s*[:=]\s*["\']([^"\']+)'
    match = re.search(pattern, resp.text)
    if match:
        csrf_token = match.group(1)
        print(f"    ✓ Token bulundu: {csrf_token[:20]}...")
    else:
        # Hidden input ara
        pattern = r'<input[^>]*name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)'
        match = re.search(pattern, resp.text, re.IGNORECASE)
        if match:
            csrf_token = match.group(1)
            print(f"    ✓ Token (hidden input): {csrf_token[:20]}...")
        else:
            print("    [!] Token bulunamadı - token'siz dene")
    
    print()
    
    # [3] Rapor talebi - Token ile
    print("[3] Rapor talebi (monthly + yearly)...")
    rapor_data = {
        'project': 'belgrad',
        'periods': 'monthly',
    }
    
    if csrf_token:
        rapor_data['csrf_token'] = csrf_token
    
    resp = session.post(
        f"{BASE_URL}/reports/management",
        data=rapor_data,
        allow_redirects=False
    )
    
    print(f"    Status: {resp.status_code}")
    
    if resp.status_code == 302:
        location = resp.headers.get('Location')
        print(f"    Redirect: {location}\n")
        
        # [4] PDF sayfasına eriş
        print("[4] PDF oluşturu...")
        if location.startswith('/'):
            pdf_url = BASE_URL + location
        else:
            pdf_url = BASE_URL + '/' + location
        
        resp = session.get(pdf_url, timeout=15)
        
        print(f"    Status: {resp.status_code}")
        print(f"    Type: {resp.headers.get('content-type')}")
        
        if resp.headers.get('content-type', '').startswith('application/pdf'):
            with open('test_rapor_web_final.pdf', 'wb') as f:
                f.write(resp.content)
            print(f"\n    ✓✓✓ PDF BAŞARIYLA OLUŞTURULDU ✓✓✓")
            print(f"    Dosya: test_rapor_web_final.pdf ({len(resp.content):,d} bytes)")
        else:
            print(f"    ✗ PDF değil")
            print(f"    İlk 300 karakter:\n{resp.text[:300]}")
    else:
        print(f"    ✗ Redirect yok: {resp.status_code}")

print("\n" + "="*70)
