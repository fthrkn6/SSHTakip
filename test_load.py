import os
import sys
sys.path.insert(0, 'c:\\Users\\ferki\\Desktop\\bozankaya_ssh_takip')

from app import create_app, db
from routes.fracas import load_fracas_data

app = create_app()

with app.app_context():
    # Session'u simule et
    from flask import session
    
    with app.test_request_context():
        from flask_login import login_user
        from models import User
        
        # Default user oluştur
        user = User(username='test', email='test@test.com', role='admin')
        
        # Sesson'u set et
        from flask import session
        session['current_project'] = 'belgrad'
        
        # FRACAS datasını yükle
        df = load_fracas_data()
        
        if df is None:
            print("❌ FRACAS verileri yüklenmedi!")
        else:
            print(f"✅ FRACAS verileri başarıyla yüklendi!")
            print(f"   Toplam satır: {len(df)}")
            print(f"   Kolonlar: {list(df.columns)[:5]}")
            print(f"\n   İlk satırın verileri:")
            print(f"   {df.iloc[0][:5]}")
