#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from app import create_app
from models import User

app = create_app()
with app.app_context():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            test_user = User.query.filter_by(email='test@test.com').first()
            if test_user:
                sess['_user_id'] = str(test_user.id)
                sess['current_project'] = 'belgrad'
        
        resp = client.get('/servis/durumu/tablo')
        if resp.status_code == 200:
            data = resp.get_json()
            print('\n✅ ENDPOINT SONUCU:')
            print(f'  Total: {data["stats"]["total"]}')
            print(f'  Operational: {data["stats"]["operational"]}')
            print('')
