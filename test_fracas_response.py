#!/usr/bin/env python
"""
FRACAS response HTML kontrol - neler render ediliyor?
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

app = create_app()

with app.test_client() as client:
    with app.app_context():
        from models import db, User, Role
        
        db.create_all()
        
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
        
        # BELGRAD
        print("=== BELGRAD RESPONSE ===\n")
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
        
        response = client.get('/fracas/?project=belgrad', follow_redirects=True)
        html = response.data.decode('utf-8')
        
        # Response'ın başını göster
        print("İLK 1000 KARAKTER:")
        print(html[:1000])
        print("\n...")
        print("\nSON 500 KARAKTER:")
        print(html[-500:])
        
        # Anahtar kelimeleri ara
        print("\n=== KEY KEYWORDS CHECK ===")
        keywords = [
            'data_available',
            'paretoModuleChart',
            'new Chart',
            'Excel Dosyası',
            'Filtreler',
            'Arıza Sayısı',
            'RAMS',
            'Pareto',
            'fracas'
        ]
        
        for keyword in keywords:
            count = html.count(keyword)
            print(f"{keyword}: {count} oluşum")
        
        # Kontrol et: Hangi template render ediliyor?
        if '</head>' in html:
            print("\n✓ HTML sayfası render ediliyor")
            if '<body>' in html:
                print("✓ Body tag'ı var")
        else:
            print("\n✗ Tam HTML sayfası değil")
        
        # Response'ı dosyaya kaydet
        with open('fracas_response_belgrad.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\nFull HTML kayıt yapıldı: fracas_response_belgrad.html")
