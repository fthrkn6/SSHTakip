#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Arıza Listesi Debug
"""

import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
import pandas as pd

app = create_app()
client = app.test_client()

print("="*70)
print("ARIZA LİSTESİ DEBUG")
print("="*70)

# 1. Giriş yap
print("\n1. Giriş yapılıyor...")
response = client.post('/login', data={
    'username': 'admin',
    'password': 'admin123'
}, follow_redirects=True)
print(f"✓ Giriş: Status {response.status_code}")

# 2. Arıza listesini aç
print("\n2. Arıza listesi açılıyor...")
response = client.get('/ariza-listesi')
print(f"✓ Sayfa açıldı: Status {response.status_code}")

response_str = response.data.decode('utf-8')

# 3. Veri kontrolü
print("\n3. HTML İçeriği Kontrolü:")
if 'excel_data' in response_str:
    print("  ✓ excel_data variable'ı var")
else:
    print("  ✗ excel_data variable'ı YOK")

if 'FRACAS ID' in response_str:
    print("  ✓ 'FRACAS ID' text'i var")
else:
    print("  ✗ 'FRACAS ID' text'i YOK")

if 'BEL25' in response_str:
    print("  ✓ 'BEL25' kaydı var")
    count = response_str.count('BEL25')
    print(f"    → Kaç kez geçiyor: {count}")
else:
    print("  ✗ 'BEL25' kaydı YOK")

if '<table' in response_str:
    print("  ✓ Tablo HTML'de mevcut")
else:
    print("  ✗ Tablo HTML'de YOK")

# 4. Excel dosyasını doğrudan kontrol et
print("\n4. Excel Dosyası Doğrudan Kontrolü:")
excel_path = r"c:\Users\ferki\Desktop\bozankaya_ssh_takip\data\belgrad\BEL25_FRACAS.xlsx"
if os.path.exists(excel_path):
    print(f"  ✓ Excel dosyası bulundu: {excel_path}")
    
    try:
        df = pd.read_excel(excel_path, sheet_name='FRACAS', header=0, engine='openpyxl')
        print(f"  ✓ Excel okundu (header=0)")
        print(f"    → Satır sayısı: {len(df)}")
        print(f"    → Sütun sayısı: {len(df.columns)}")
        print(f"    → Sütunlar: {list(df.columns)[:5]}")
        
        # FRACAS ID sütununu bul
        fracas_col = None
        for col in df.columns:
            if 'fracas' in col.lower() and 'id' in col.lower():
                fracas_col = col
                break
        
        if fracas_col:
            print(f"  ✓ FRACAS ID sütunu bulundu: '{fracas_col}'")
            print(f"    → İlk 5 ID: {df[fracas_col].head().tolist()}")
        else:
            print(f"  ✗ FRACAS ID sütunu bulunamadı")
            
    except Exception as e:
        print(f"  ✗ Excel okunamadı: {e}")
else:
    print(f"  ✗ Excel dosyası bulunamadı")

print("\n" + "="*70)
