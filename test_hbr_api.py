#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API üzerinden HBR oluştur ve dosya adlandırmasını kontrol et
"""

import requests
import json
import time
from pathlib import Path

# Test verileri
BASE_URL = "http://127.0.0.1:5000"
PROJECT_CODE = "BELGRAD"

# Arıza oluştur POST isteği
test_failure_data = {
    "equpment_code": "1531",  # Araç numarası
    "sistem": "Motor",  # Sistem adı
    "ariza_tipi": "Mekanik",  # Arıza tipi
    "arizakodu": "M001",  # Arıza kodu
    "sinyaltipi": "Sensor",  # Sinyal tipi
    "sinyaladi": "Sıcaklık Sensörü",  # Sinyal adı
    "tanimlama": "Sıcaklık sensörü arızalandı",  # Tanımlama
    "detay": "Sensör sıcaklık ölçümü yapamıyor",  # Detay
}

print("🧪 HBR Dosya Adlandırması Test")
print("=" * 60)

# HBR klasörünü kontrol et (test öncesi)
hbr_dir = Path(f"logs/{PROJECT_CODE}/HBR")
print(f"\n📁 HBR Klasörü: {hbr_dir}")

if hbr_dir.exists():
    existing_bel25 = list(hbr_dir.glob("BEL25-NCR-*"))
    existing_boz = list(hbr_dir.glob("BOZ-NCR-*"))
    print(f"   BEL25-NCR dosyaları: {len(existing_bel25)}")
    print(f"   BOZ-NCR dosyaları: {len(existing_boz)} (eski)")
    
    if existing_bel25:
        latest = sorted(existing_bel25)[-1]
        print(f"   ✅ Son BEL25-NCR: {latest.name}")
else:
    print(f"   ❌ HBR klasörü bulunamadı!")

print("\n📤 Arıza Oluşturma API'si test ediliyor...")
print(f"   URL: {BASE_URL}/dashboard/quikAdd")
print(f"   Method: POST")

try:
    response = requests.post(
        f"{BASE_URL}/dashboard/quikAdd",
        json=test_failure_data,
        timeout=10
    )
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   Response: {result.get('message', 'Başarılı')}")
        
        # 2 saniyelik süre ver dosyanın yazılması için
        time.sleep(2)
        
        # HBR klasörünü yeniden kontrol et
        print("\n✅ Test sonrası HBR klasörü:")
        existing_bel25_after = list(hbr_dir.glob("BEL25-NCR-*"))
        print(f"   BEL25-NCR dosyaları: {len(existing_bel25_after)}")
        
        if len(existing_bel25_after) > len(existing_bel25):
            new_file = sorted(existing_bel25_after)[-1]
            print(f"   🎯 YENİ DOSYA: {new_file.name}")
            print(f"   ✅ BEL25-NCR adlandırması ONAYLANDI!")
        else:
            print(f"   ❌ Yeni dosya oluşturulmadı")
    else:
        print(f"   ⚠️ API Hatası: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
