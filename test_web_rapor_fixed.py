#!/usr/bin/env python3
"""Test rapor web - Doğru form data"""
import requests

BASE_URL = "http://127.0.0.1:5000"

print("\n" + "="*70)
print("WEB RAPOR TESTI - Doğru Form Data")
print("="*70 + "\n")

with requests.Session() as session:
    # [1] Login
    print("[1] Login...")
    login_data = {
        'username': 'admin',
        'password': 'password1'
    }
    
    resp = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    if resp.status_code != 200:
        print(f"    ✗ Login başarısız: {resp.status_code}")
        exit(1)
    print("    ✓ Login başarılı\n")
    
    # [2] Rapor talebi - Form array göndermesi
    print("[2] BELGRAD + monthly rapor (form array)...")
    
    # Doğru format: multiple values aynı key'e
    rapor_data = [
        ('project', 'belgrad'),
        ('periods', 'monthly'),
        ('periods', 'yearly')  # Çoklu periyot seçimi
    ]
    
    # İLK: Management 'ye POST yap (form submit)
    resp = session.post(
        f"{BASE_URL}/reports/management",
        data=rapor_data,
        allow_redirects=False  # Redirect'i görmek için
    )
    
    print(f"    Management POST Status: {resp.status_code}")
    
    if resp.status_code == 302:  # Redirect
        location = resp.headers.get('Location')
        print(f"    Redirect to: {location}\n")
        
        # [3] Redirect URL'e git (PDF oluşturulacak)
        print("[3] PDF oluşturma sayfasına eriş...")
        
        # Redirect URL tam yol olabilir kısa olabilir
        if location.startswith('/'):
            pdf_url = BASE_URL + location
        else:
            pdf_url = location
        
        resp = session.get(pdf_url, timeout=15)
        
        print(f"    Status: {resp.status_code}")
        print(f"    Content-Type: {resp.headers.get('content-type', 'N/A')}")
        
        if resp.headers.get('content-type', '').startswith('application/pdf'):
            with open('test_web_rapor_success.pdf', 'wb') as f:
                f.write(resp.content)
            print(f"    ✓ PDF başarıyla oluşturuldu!")
            print(f"    Dosya: test_web_rapor_success.pdf ({len(resp.content)} bytes)")
        else:
            print(f"    ✗ PDF bekleniyordu ama: {resp.headers.get('content-type')}")
            if len(resp.content) < 1000:
                print(f"\n    Response:\n{resp.text[:500]}")
    else:
        print(f"    ✗ Redirect olmadı: {resp.status_code}")
        print(f"    Response:\n{resp.text[:500]}")

print("\n" + "="*70)
