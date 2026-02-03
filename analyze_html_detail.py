#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()
client = app.test_client()

# Giriş
client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)

# Arıza listesi al
response = client.get('/ariza-listesi')
html = response.data.decode('utf-8')

# Kritik bilgiler ara
print("=== HTML ANALİZİ ===\n")
print(f"Status: {response.status_code}")
print(f"HTML boyutu: {len(html)} byte\n")

# excel_data kontrolü
if 'excel_data' in html:
    print("✓ 'excel_data' template değişkeni HTML'de var")
    # Değerini çıkarmaya çal
    if 'excel_data=True' in html or 'excel_data = True' in html:
        print("  → Değeri: True")
    elif 'excel_data=False' in html or 'excel_data = False' in html:
        print("  → Değeri: False")
    else:
        print("  → Değeri bilinmiyor")
else:
    print("✗ 'excel_data' variable'ı HTML'de YOK")

# Veri kontrolü
if '<tbody>' in html:
    print("\n✓ Tablo body'si var")
    # İçindeki satırları say
    import re
    rows = re.findall(r'<tr[^>]*>', html)
    print(f"  → Toplam <tr> tag'ı: {len(rows)}")
    
    # Veri satırlarını say (detail olmayan)
    data_rows = re.findall(r'<tr style="cursor: pointer;"', html)
    print(f"  → Veri satırları: {len(data_rows)}")
else:
    print("\n✗ Tablo body'si YOK")

# FRACAS ID badge'lerini kontrol et
fracas_badges = re.findall(r'<span class="badge[^>]*>([A-Z0-9\-]+)</span>', html)
print(f"\n✓ Bulundum FRACAS ID'ler:")
for i, badge in enumerate(fracas_badges[:10], 1):
    print(f"  {i}. {badge}")

if len(fracas_badges) == 0:
    print("  ✗ Hiç badge bulunamadı!")
