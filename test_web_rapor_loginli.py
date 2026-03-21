#!/usr/bin/env python3
"""Test rapor web - login ile"""
import requests

BASE_URL = "http://127.0.0.1:5000"

print("\n" + "="*70)
print("WEB RAPOR TESTI - Login ile")
print("="*70 + "\n")

with requests.Session() as session:
    # [1] Login page'e eriş
    print("[1] Login sayfasına eriş...")
    resp = session.get(f"{BASE_URL}/")
    
    if 'login' in resp.text.lower():
        print("    ✓ Login sayfası resmiydi")
        
        # [2] Credentials ile login
        print("[2] Login...")
        login_data = {
            'username': 'admin',
            'password': 'password1'
        }
        
        resp = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
        print(f"    Status: {resp.status_code}")
        
        if 'logout' in resp.text.lower() or resp.status_code == 200:
            print("    ✓ Login başarılı\n")
            
            # [3] Rapor talebi
            print("[3] BELGRAD + monthly rapor...")
            rapor_data = {
                'project': 'belgrad',
                'periods': 'monthly'
            }
            
            resp = session.post(
                f"{BASE_URL}/reports/management",
                data=rapor_data,
                allow_redirects=True,
                timeout=10
            )
            
            print(f"    Status: {resp.status_code}")
            print(f"    Content-Type: {resp.headers.get('content-type', 'N/A')}")
            
            if resp.headers.get('content-type', '').startswith('application/pdf'):
                with open('test_web_raporLoggedIn.pdf', 'wb') as f:
                    f.write(resp.content)
                print(f"    ✓ PDF kaydedildi: {len(resp.content)} bytes")
                print("    Dosya: test_web_raporLoggedIn.pdf")
            else:
                print(f"    ✗ PDF değil: {resp.headers.get('content-type')}")
                if len(resp.content) < 1000:
                    print(f"    Response: {resp.text[:500]}")
        else:
            print("    ✗ Login başarısız")
            print(f"    Status: {resp.status_code}")
    else:
        print("    [!] Login sayfası değil - auth gerekli mi?")
        print(f"    Sayfada 'login' yok")

print("\n" + "="*70)
