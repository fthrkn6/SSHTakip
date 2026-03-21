#!/usr/bin/env python3
"""Test rapor web üzerinden - Tüm projeler"""
import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

print("\n" + "="*70)
print("WEB RAPOR TESTI")
print("="*70 + "\n")

# Flask sunucusu çalışıyor mu?
print("[1] Flask sunucusu kontrol...")
try:
    resp = requests.get(f"{BASE_URL}/", timeout=5)
    if resp.status_code in [200, 302]:  # 302 login redirect
        print("    ✓ Flask çalışıyor\n")
    else:
        print(f"    ✗ Durum: {resp.status_code}\n")
except Exception as e:
    print(f"    ✗ Bağlantı hatası: {e}\n")
    sys.exit(1)

# Tüm projeleri test et
all_projects = ['belgrad', 'istanbul', 'kayseri', 'kocaeli', 'gebze', 'samsun', 'iasi', 'timisoara']

print("[2] İndividual proje raporları test...")
test_count = 0
for project in all_projects[:2]:  # İlk 2'yi test et
    try:
        # Form verisi ile POST
        data = {
            'project': project,
            'periods': ['monthly']  # checkbox değeri
        }
        
        # Session kultan login gerek
        with requests.Session() as session:
            # Önce ana sayfama git (session oluştur)
            resp = session.get(f"{BASE_URL}/")
            
            # Report oluştur
            resp = session.post(f"{BASE_URL}/reports/management", data=data, allow_redirects=True, timeout=10)
            
            if resp.status_code == 200 and resp.headers.get('content-type', '').startswith('application/pdf'):
                file_size = len(resp.content)
                print(f"    ✓ {project.upper():10s} - {file_size:6,d} bytes")
                test_count += 1
                
                # Dosya kaydettir
                with open(f'rapor_web_{project}.pdf', 'wb') as f:
                    f.write(resp.content)
            else:
                ct = resp.headers.get('content-type', 'unknown')
                print(f"    ✗ {project.upper():10s} - Status: {resp.status_code}, Type: {ct[:30]}")
    except Exception as e:
        print(f"    ✗ {project.upper():10s} - Hata: {str(e)[:40]}")

print(f"\n    Başarı: {test_count}/2\n")

# Tüm projeler raporu test et
print("[3] Tüm Projeler raporu test...")
try:
    data = {
        'project': 'all',
        'periods': ['monthly']
    }
    
    with requests.Session() as session:
        resp = session.get(f"{BASE_URL}/")
        resp = session.post(f"{BASE_URL}/reports/management", data=data, allow_redirects=True, timeout=15)
        
        if resp.status_code == 200 and resp.headers.get('content-type', '').startswith('application/pdf'):
            file_size = len(resp.content)
            print(f"    ✓ TUM PROJELER - {file_size:,d} bytes")
            
            with open('rapor_web_all_projects.pdf', 'wb') as f:
                f.write(resp.content)
            print(f"    ✓ Kaydedildi: rapor_web_all_projects.pdf")
        else:
            ct = resp.headers.get('content-type', 'unknown')
            print(f"    ✗ Status: {resp.status_code}, Type: {ct[:30]}")
except Exception as e:
    print(f"    ✗ Hata: {str(e)[:60]}")

print("\n" + "="*70 + "\n")
