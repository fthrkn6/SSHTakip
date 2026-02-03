import requests
from requests.auth import HTTPBasicAuth

# Session yarat
session = requests.Session()

# Login URL'sine istek gönder  
login_url = "http://localhost:5000/login"
login_data = {
    "username": "admin",
    "password": "admin123"
}

print("1. Logging in...")
r1 = session.post(login_url, data=login_data, allow_redirects=True)
print(f"   Status: {r1.status_code}")
print(f"   Redirected: {r1.url}")

# Şimdi yeni-ariza-bildir'e git
print("\n2. GET /yeni-ariza-bildir...")
r2 = session.get("http://localhost:5000/yeni-ariza-bildir")
print(f"   Status: {r2.status_code}")

if "BOZ-BEL25-FF-" in r2.text:
    # FRACAS ID'yi bul
    import re
    match = re.search(r'BOZ-BEL25-FF-\d{3}', r2.text)
    if match:
        print(f"   FRACAS ID bulundu: {match.group(0)}")
    else:
        print("   FRACAS ID bulunamadı!")
else:
    print("   FRACAS ID text'te yok!")

# İlk 50 satırı yazdır (debug)
print(f"\n   Response ilk 1000 char:\n{r2.text[:1000]}")
