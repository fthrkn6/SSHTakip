#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Arıza Listesi - Excel Veri Test
"""

from app import create_app

app = create_app()
client = app.test_client()

print("="*70)
print("ARIZA LİSTESİ EXCEL TEST")
print("="*70)

# 1. Giriş yap
print("\n1. Admin giriş yapılıyor...")
response = client.post('/login', data={
    'username': 'admin',
    'password': 'admin123'
}, follow_redirects=True)
print(f"✓ Giriş sonucu: Status {response.status_code}")

# 2. Arıza listesini aç
print("\n2. Arıza listesi açılıyor (/ariza-listesi)...")
response = client.get('/ariza-listesi')
print(f"✓ Sayfa açıldı: Status {response.status_code}")

html = response.data.decode('utf-8')

# 3. Veri kontrolü
print("\n3. Verileri Kontrol Et:")
print(f"  ✓ HTML boyutu: {len(html)} bytes")

# FRACAS kayıtlarını ara
kayitlar = ['BEL25-001', 'BEL25-002', 'BEL25-003', 'BOZ-BEL25-FF-036']
for kayit in kayitlar:
    if kayit in html:
        print(f"  ✓ {kayit} BULUNDU")
    else:
        print(f"  ✗ {kayit} BULUNAMADI")

# Tablo satırlarını say
if '<table' in html:
    print(f"  ✓ Tablo HTML'de var")
    # <tr> başladığını say - tabloda kaç satır?
    tr_count = html.count('<tr')
    print(f"    → <tr> tag'ları: {tr_count}")
else:
    print(f"  ✗ Tablo HTML'de YOK")

print("\n" + "="*70)
