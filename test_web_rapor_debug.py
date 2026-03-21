#!/usr/bin/env python3
"""Test rapor web üzerinden - Debug"""
import requests
import sys
import io

BASE_URL = "http://127.0.0.1:5000"

print("\n" + "="*70)
print("WEB RAPOR TESTI - DEBUG")
print("="*70 + "\n")

# Test 1: Basit request
print("[1] BELGRAD + monthly rapor talebi...\n")

with requests.Session() as session:
    # POST data - form checkbox şeklinde
    data = {
        'project': 'belgrad',
        'periods': 'monthly'  # String olarak bir periyot
    }
    
    print(f"POST data: {data}")
    print(f"Hedef: {BASE_URL}/reports/management\n")
    
    try:
        resp = session.post(
            f"{BASE_URL}/reports/management",
            data=data,
            allow_redirects=True,
            timeout=10
        )
        
        print(f"Status Code: {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('content-type', 'N/A')}")
        print(f"Content Length: {len(resp.content)} bytes\n")
        
        # Eğer HTML ise, hata mesajını çek
        if resp.headers.get('content-type', '').startswith('text/html'):
            # HTML içinde flash mesajı var mı?
            if 'Rapor' in resp.text or 'rapor' in resp.text:
                print("HTML Yanıt bulundu - Flask render etmiş")
                # Hata yaz
                lines = resp.text.split('\n')
                for i, line in enumerate(lines):
                    if 'rapor' in line.lower() or 'error' in line.lower() or 'hata' in line.lower():
                        print(f"  {line[:100]}")
            else:
                print("HTML redirect - session/login problemi olabilir")
        
        elif resp.headers.get('content-type', '').startswith('application/pdf'):
            print("✓ PDF başarıyla oluşturuldu!")
            
            # PDF'yi kaydet
            with open('test_web_rapor_output.pdf', 'wb') as f:
                f.write(resp.content)
            print("  Kaydedildi: test_web_rapor_output.pdf")
        
        else:
            print("Bilinmeyen content type!")
            print(f"İlk 200 karakter: {resp.text[:200]}")
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*70)
