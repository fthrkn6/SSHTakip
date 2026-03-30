#!/usr/bin/env python
"""
FRACAS render test - Template ve data kontrol
"""

import os
import sys
import io
import logging
sys.path.insert(0, os.path.dirname(__file__))

# Unicode output fix
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app
from flask import session

# Logging setup - capture
logging.basicConfig(level=logging.DEBUG, format='[%(name)s] %(message)s')

app = create_app()

# Test Client oluştur
with app.test_client() as client:
    # Login - User oluştur ve giriş yap
    with app.app_context():
        from models import db, User, Role
        
        # Veritabanı session'ı temizle
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
            print("* Test user oluşturuldu")
        
        # BELGRAD TEST
        print("\n=== BELGRAD TEST ===")
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
        
        response = client.get('/fracas/?project=belgrad', follow_redirects=True)
        html = response.data.decode('utf-8')
        
        print(f"Status: {response.status_code}")
        print(f"Response boyutu: {len(html)} bytes")
        
        # Check key elements
        has_excel_warning = 'Excel Dosyası Bulunamadı' in html
        has_paretoModule = 'paretoModuleChart' in html
        has_chart_script = 'new Chart' in html
        
        print(f"Excel Warning (veri yok): {has_excel_warning}")
        print(f"paretoModuleChart canvas: {has_paretoModule}")
        print(f"Chart script: {has_chart_script}")
        
        if has_excel_warning:
            print("SORUN: Excel dosyası bulunamıyor!")
            # Dosya kontrolü
            belgrad_path = r'C:\Users\fatiherkin\Desktop\bozankaya_ssh_takip\logs\belgrad\ariza_listesi\Fracas_BELGRAD.xlsx'
            print(f"Dosya var mı? {os.path.exists(belgrad_path)}")
        
        if has_paretoModule and has_chart_script:
            print("✓ Grafikler render ediliyor!")
            # Data kontrolü
            if '[1' in html or 'count' in html:
                print("✓ Chart data HTML'de bulundu")
        
        # TIMIŞOARA TEST
        print("\n=== TİMİŞOARA TEST ===")
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
        
        response = client.get('/fracas/?project=timisoara', follow_redirects=True)
        html = response.data.decode('utf-8')
        
        print(f"Status: {response.status_code}")
        print(f"Response boyutu: {len(html)} bytes")
        
        has_excel_warning = 'Excel Dosyası Bulunamadı' in html
        has_paretoModule = 'paretoModuleChart' in html
        has_chart_script = 'new Chart' in html
        
        print(f"Excel Warning (veri yok): {has_excel_warning}")
        print(f"paretoModuleChart canvas: {has_paretoModule}")
        print(f"Chart script: {has_chart_script}")
        
        if has_excel_warning:
            print("SORUN: Excel dosyası bulunamıyor!")
            timisoara_path = r'C:\Users\fatiherkin\Desktop\bozankaya_ssh_takip\logs\timisoara\ariza_listesi\Fracas_TIMISOARA.xlsx'
            print(f"Dosya var mı? {os.path.exists(timisoara_path)}")
        
        if has_paretoModule and has_chart_script:
            print("✓ Grafikler render ediliyor!")
