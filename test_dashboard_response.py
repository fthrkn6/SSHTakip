#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json

# Flask'ın açması için 2 saniye bekle
import time
time.sleep(2)

# Dashboard'ı test et
try:
    response = requests.get('http://localhost:5000/dashboard', cookies={'session': 'test'})
    
    if 'tramvay' in response.text:
        # HTML'den tramvay count çıkart
        import re
        # Debug comment'teki sayı
        match = re.search(r'DEBUG: tramvaylar count = (\d+)', response.text)
        if match:
            count = match.group(1)
            print(f"[RESPONSE] Tramvay count in template: {count}")
        
        # Tramvay grid'deki card sayısı
        card_count = response.text.count('tramvay-card')
        print(f"[RESPONSE] Tramvay card HTML elements: {card_count}")
        
        # İlk 5 araç kodunu çıkart
        matches = re.findall(r'data-vehicle="([^"]+)"', response.text)
        print(f"[RESPONSE] Vehicle codes: {matches[:10]}")
    else:
        print("[RESPONSE] No tramvay data found")
        print(response.status_code)
except Exception as e:
    print(f"[ERROR] {e}")
