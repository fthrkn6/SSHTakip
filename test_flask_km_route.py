#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask uygulamasındaki KM update route'unu test et
"""
import sys
sys.path.insert(0, r'c:\Users\fatiherkin\Desktop\bozankaya_ssh_takip')

from app import app, db
from models import User, Equipment
from flask import session
from werkzeug.datastructures import ImmutableMultiDict

print("\n" + "="*70)
print("KM GÜNCELLEME ROUTE TEST")
print("="*70)

with app.app_context():
    # Admin user oluştur/bul
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print("❌ Admin user bulunamadı. Test yapılamadı.")
        sys.exit(1)
    
    print(f"\n✅ Admin user bulundu: {admin.username}")
    
    # Başlangıç kontrolü
    eq = Equipment.query.filter_by(id=1).first()
    print(f"\nBAŞLANGIÇ: Equipment id=1")
    print(f"  - code: {eq.equipment_code}")
    print(f"  - km: {eq.current_km}")
    
    # Test isteği yapalım
    print(f"\nTEST: tram_id='1531', new_km='777' gönder")
    with app.test_client() as client:
        # Login önce
        login_response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        
        if login_response.status_code == 200:
            print("  ✅ Login başarılı")
            
            # KM update
            update_response = client.post('/tramvay-km/guncelle', data={
                'tram_id': '1531',  # Equipment code
                'current_km': '777',
                'notes': 'Test güncelleme'
            }, follow_redirects=True)
            
            print(f"  Response status: {update_response.status_code}")
            
            # Response'da mesajı ara
            if b"KM bilgileri kaydedildi" in update_response.data:
                # Hangi numara yazıyor?
                html_text = update_response.data.decode('utf-8')
                import re
                match = re.search(r'✅\s*(\d+|1531)\s*KM bilgileri', html_text)
                if match:
                    number = match.group(1)
                    print(f"  📝 Mesaj: ✅ {number} KM bilgileri kaydedildi")
                    if number == '1531':
                        print(f"     ✅ DOĞRU - 1531 yazıyor")
                    elif number == '1':
                        print(f"     ❌ HATA - 1 yazıyor (yanlış)")
        else:
            print(f"  ❌ Login başarısız: {login_response.status_code}")
    
    # Final kontrolü
    db.session.refresh(eq)
    print(f"\nSONUÇ: Equipment id=1")
    print(f"  - code: {eq.equipment_code}")
    print(f"  - km: {eq.current_km}")
    
    if eq.current_km == 777:
        print(f"\n✅ SİSTEM DOĞRU ÇALIŞIYOR - km=777 yazıldı")
    else:
        print(f"\n⚠️  km değişmedi: {eq.current_km}")

print("\n" + "="*70 + "\n")
