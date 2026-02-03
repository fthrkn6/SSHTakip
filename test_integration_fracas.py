#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Yeni Arıza Bildir - İntegrasyon Testi
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Equipment
from datetime import datetime

app = create_app()

with app.app_context():
    # Veritabanı tablolarını oluştur
    db.create_all()
    
    # Kullanıcı oluştur (eğer yoksa)
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin kullanıcısı oluşturuldu")
    else:
        print("✓ Admin kullanıcısı zaten var")
    
    # Test ekimanı oluştur (eğer yoksa)
    test_equipment = Equipment.query.filter_by(equipment_code='TEST-001').first()
    if not test_equipment:
        test_equipment = Equipment(
            equipment_code='TEST-001',
            name='Test Tramvay',
            equipment_type='arac',
            manufacturer='Test',
            model='Model-1',
            status='active'
        )
        db.session.add(test_equipment)
        db.session.commit()
        print(f"✓ Test ekimanı oluşturuldu (ID: {test_equipment.id})")
    else:
        print(f"✓ Test ekimanı zaten var (ID: {test_equipment.id})")

print("\n" + "="*70)
print("FLASK TEST CLIENT İLE ARIZA EKLEME")
print("="*70)

# Flask test client oluştur
client = app.test_client()

# 1. Giriş yap
print("\n1. Giriş Yapılıyor...")
response = client.post('/login', data={
    'username': 'admin',
    'password': 'admin123'
}, follow_redirects=True)

if response.status_code == 200:
    print("✓ Giriş başarılı (Status: 200)")
else:
    print(f"✗ Giriş başarısız (Status: {response.status_code})")

# 2. Yeni Arıza formunu aç
print("\n2. Yeni Arıza Formu Açılıyor...")
response = client.get('/arizalar/ekle')

if response.status_code == 200:
    print("✓ Form açıldı (Status: 200)")
    
    # FRACAS ID'nin form'da gösterilip gösterilmediğini kontrol et
    if b'FRACAS ID' in response.data or b'BOZ-BEL25-FF' in response.data:
        print("✓ FRACAS ID formlarda gösteriliyor")
    else:
        print("✗ FRACAS ID formlarda gösterilmiyor")
else:
    print(f"✗ Form açılamadı (Status: {response.status_code})")

# 3. Yeni Arıza Ekle
print("\n3. Yeni Arıza Ekleniyor...")
with app.app_context():
    equipment = Equipment.query.filter_by(equipment_code='TEST-001').first()
    if equipment:
        response = client.post('/arizalar/ekle', data={
            'arac_id': equipment.id,
            'failure_date': datetime.now().strftime('%Y-%m-%dT%H:%M'),
            'description': 'Test arızası - Sistem testi için oluşturuldu',
            'severity': 'critical',
            'failure_type': 'elektronik'
        }, follow_redirects=True)
        
        if response.status_code == 200:
            print("✓ Arıza eklendi (Status: 200)")
            
            # Response'ta başarı mesajı kontrol et
            if b'FRACAS ID' in response.data and b'BOZ-BEL25-FF' in response.data:
                print("✓ Başarılı sonuç mesajında FRACAS ID görünüyor")
            else:
                print("ℹ Sonuç mesajı kontrol edin")
        else:
            print(f"✗ Arıza eklenemedi (Status: {response.status_code})")
    else:
        print("✗ Test ekimanı bulunamadı")

print("\n" + "="*70)
print("EXCEL DOSYASINI KONTROL ET")
print("="*70)

import pandas as pd

excel_path = r"c:\Users\ferki\Desktop\bozankaya_ssh_takip\data\belgrad\BEL25_FRACAS.xlsx"
df = pd.read_excel(excel_path, sheet_name='FRACAS', header=0, engine='openpyxl')
df.columns = df.columns.astype(str).str.replace('\n', ' ', regex=False).str.strip()

print(f"\n✓ Excel dosyası okundu")
print(f"  Toplam satır: {len(df)}")
print(f"  Yeni satırlar:")

# Son 3 satırı göster
for idx in range(max(0, len(df)-3), len(df)):
    fracas_id_col = None
    for col in df.columns:
        if 'fracas' in col.lower() and 'id' in col.lower():
            fracas_id_col = col
            break
    
    if fracas_id_col:
        fracas_id = df.iloc[idx][fracas_id_col]
        desc_val = ''
        for col in df.columns:
            if 'ariza' in col.lower() and 'tanim' in col.lower():
                desc_val = str(df.iloc[idx][col])[:50]
                break
        print(f"    Satır {idx+2}: {fracas_id} - {desc_val}")

print("\n" + "="*70)
print("✓ Test Tamamlandı")
print("="*70)
