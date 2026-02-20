#!/usr/bin/env python
from app import create_app, db
from models import ServiceStatus

app = create_app()
with app.test_client() as client:
    # Login
    client.post('/login', data={'username': 'testuser', 'password': 'password'})
    
    # Belirli bir tarih seç ve tüm araçları servise al
    test_date = '2026-02-10'
    
    response = client.post('/servis-durumu/toplu-servise-al',
        json={
            'tram_ids': ['1531', '1532'],
            'tarih': test_date
        },
        content_type='application/json'
    )
    
    print(f'Response Status: {response.status_code}')
    data = response.get_json()
    print(f'Message: {data.get("message")}')
    
    # Kontrol et
    with app.app_context():
        records = ServiceStatus.query.filter_by(date=test_date).all()
        print(f'Records for {test_date}:')
        for r in records:
            print(f'  - {r.tram_id}: {r.status}')
