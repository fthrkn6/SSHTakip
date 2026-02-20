#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug dashboard verilerini kontrol et"""

import os
import sys
from datetime import datetime

# Add app directory to path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

from app import create_app
from models import db, Equipment, ServiceStatus

app = create_app()

with app.app_context():
    print("=" * 80)
    print("DASHBOARD VERİ KONTROL")
    print("=" * 80)
    
    # 1. ServiceStatus'ten bugünün verilerini çek
    today = str(datetime.now().date())
    print(f"\n📅 Tarih: {today}")
    
    service_status_records = ServiceStatus.query.filter_by(date=today).all()
    print(f"✅ ServiceStatus kayıtları: {len(service_status_records)}")
    
    status_dict = {record.tram_id: record.status for record in service_status_records}
    print(f"   Status dict: {len(status_dict)} tramvay")
    
    # 2. Equipment'lar
    all_equipment = Equipment.query.filter_by(parent_id=None).all()
    print(f"\n✅ Equipment (parent_id=None): {len(all_equipment)}")
    
    # 3. İlk 5 Equipment'ı kontrol et
    print("\n📊 İLK 5 TRAMVAY:")
    for i, eq in enumerate(all_equipment[:5]):
        status_from_db = status_dict.get(eq.equipment_code, 'Servis')
        print(f"   {i+1}. ID={eq.id}, Code={eq.equipment_code}, Name={eq.name}")
        print(f"      current_km={getattr(eq, 'current_km', 'YOĞK')}, total_km={getattr(eq, 'total_km', 'YOĞK')}")
        print(f"      ServiceStatus: {status_from_db}")
    
    # 4. Dashboard route'u test et
    print("\n" + "=" * 80)
    print("DASHBOARD ROUTE TEST")
    print("=" * 80)
    
    client = app.test_client()
    
    # Login olmadan test et (redirect yapabilir)
    response = client.get('/dashboard')
    print(f"\n❓ /dashboard GET status: {response.status_code}")
    
    if response.status_code == 302:
        print("   ⚠️  Redirect (302) - Login gerekli")
        location = response.headers.get('Location', 'N/A')
        print(f"   Yönlendirme: {location}")
    elif response.status_code == 200:
        print("   ✅ 200 OK - Sayfa döndü")
        # HTML'de 'tramvaylar' var mı kontrol et
        if b'tramvaylar' in response.data:
            print("   ✅ 'tramvaylar' değişkeni template'e gönderilmiş")
        else:
            print("   ❌ 'tramvaylar' değişkeni template'e gönderilememiş!")
        
        # HTML'de fleet bölümü var mı
        if b'Tramvay Filosu' in response.data or b'tramvay' in response.data.lower():
            print("   ✅ Tramvay Filosu bölümü HTML'de var")
        else:
            print("   ❌ Tramvay Filosu bölümü HTML'de yok!")
    else:
        print(f"   ❌ Hata: {response.status_code}")
    
    # 5. app.py'deki tramvay_statuses'ı çek (simulate)
    print("\n" + "=" * 80)
    print("TRAMVAY_STATUSES SIMULATION")
    print("=" * 80)
    
    tramvay_statuses = []
    for tramvay in all_equipment:
        status_from_db = status_dict.get(tramvay.equipment_code, 'Servis')
        
        if status_from_db == 'Servis':
            status_display = 'aktif'
        elif status_from_db == 'İşletme Kaynaklı Servis Dışı':
            status_display = 'bakim'
        else:
            status_display = 'ariza'
        
        tramvay_statuses.append({
            'id': tramvay.id,
            'equipment_code': tramvay.equipment_code,
            'name': tramvay.name,
            'location': tramvay.location if hasattr(tramvay, 'location') else '',
            'total_km': tramvay.total_km if hasattr(tramvay, 'total_km') else 0,
            'current_km': tramvay.current_km if hasattr(tramvay, 'current_km') else 0,
            'status': status_display,
            'status_db': status_from_db
        })
    
    print(f"✅ tramvay_statuses: {len(tramvay_statuses)} kayıt")
    print(f"\n📋 İLK 3 KAYIT:")
    for i, ts in enumerate(tramvay_statuses[:3]):
        print(f"   {i+1}. {ts['equipment_code']} - {ts['status']} - {ts['current_km']}km")
    
    # 6. Status dağılımı
    aktif = sum(1 for t in tramvay_statuses if t['status'] == 'aktif')
    bakim = sum(1 for t in tramvay_statuses if t['status'] == 'bakim')
    ariza = sum(1 for t in tramvay_statuses if t['status'] == 'ariza')
    
    print(f"\n📊 STATUS DAĞILIMI:")
    print(f"   🟢 Aktif (Servis): {aktif}")
    print(f"   🟠 Bakımda: {bakim}")
    print(f"   🔴 Arızalı: {ariza}")
    print(f"   ─────────────────")
    print(f"   TOPLAM: {len(tramvay_statuses)}")
    
    print("\n" + "=" * 80)
