#!/usr/bin/env python
"""
FRACAS route render test - Data ve template render kontrolü
"""

import os
import sys
import io
sys.path.insert(0, os.path.dirname(__file__))

# Unicode output fix
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app
from flask import session

app = create_app()

# Test Client oluştur
with app.test_client() as client:
    # Login - User oluştur ve giriş yap
    with app.app_context():
        from models import db, User, Role
        
        # Veritabanı session'ı temzile
        db.create_all()
        
        # Test user oluştur (varsa hata yok)
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            user_role = Role.query.filter_by(name='operator').first()
            if not user_role:
                user_role = Role(name='operator', description='Operator')
                db.session.add(user_role)
                db.session.commit()
            
            test_user = User(
                username='testuser',
                email='test@test.com',
                password_hash='testpass123'
            )
            test_user.roles.append(user_role)
            db.session.add(test_user)
            db.session.commit()
            print("✓ Test user oluşturuldu: testuser")
        
        # Login yap
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        if response.status_code == 200:
            print(f"✓ Login başarılı (status: {response.status_code})")
        else:
            print(f"✗ Login başarısız (status: {response.status_code})")
            print(f"Response: {response.data[:500]}")
            sys.exit(1)
        
        # FRACAS page'e erişim (belgrad) - follow_redirects ile
        print("\n--- BELGRAD FRACAS REQUESİ ---")
        response = client.get('/fracas/?project=belgrad', follow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        html = response.data.decode('utf-8')
        
        # Debug: response'ın başını göster
        print(f"[DEBUG] Response başlangıcı:\n{html[:500]}\n")
        if 'data_available' in html or 'paretoModuleChart' in html:
            print("✓ Template gösterildi (canvas elementleri bulundu)")
            
            # Check for specific elements
            if 'paretoModuleChart' in html:
                print("✓ paretoModuleChart canvas bulundu")
            else:
                print("✗ paretoModuleChart canvas bulunamadı")
            
            if 'new Chart(document.getElementById(\'paretoModuleChart\')' in html:
                print("✓ paretoModuleChart script bulundu")
            else:
                print("✗ paretoModuleChart script bulunamadı")
            
            # Check data arrays
            if '"pareto_labels_module"' in html or 'pareto_labels_module' in html:
                print("✓ pareto_labels_module template'de bulundu")
                # Extract the JSON array
                import re
                match = re.search(r'\[.*?"MC".*?\]', html)
                if match:
                    print(f"  Data örneği: {match.group(0)[:100]}...")
            else:
                print("✗ pareto_labels_module template'de bulunamadı")
            
            # Check for warning message
            if 'Excel Dosyası Bulunamadı' in html:
                print("⚠ Template uyarı gösteriyor - veri yok")
            
            # Dosya boyutu
            print(f"\nResponse boyutu: {len(html)} bytes")
            
        else:
            print("✗ HTML'de beklenen elementler bulunamadı")
        
        # Timişoara test
        print("\n--- TİMİŞOARA FRACAS REQUESİ ---")
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['_flashes'] = []
        
        response = client.get('/fracas/?project=timisoara', follow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        html = response.data.decode('utf-8')
        
        if 'paretoModuleChart' in html:
            print("✓ Template gösterildi (canvas elementleri bulundu)")
            
            if 'Excel Dosyası Bulunamadı' in html:
                print("⚠ Template uyarı gösteriyor - veri yok")
            else:
                print("✓ Uyarı yok - veri yüklendi")
                
                if 'new Chart(document.getElementById(\'paretoModuleChart\')' in html:
                    print("✓ Chart scripts renders'ı bulundu")
                else:
                    print("✗ Chart script bulunamadı")
        else:
            print("✗ Canvas bulunamadı")
        
        print(f"Response boyutu: {len(html)} bytes")
