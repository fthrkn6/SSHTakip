#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from app import create_app
from models import db, User, Equipment, ServiceStatus
from utils_project_excel_store import read_all_km, upsert_service_status, read_service_status_by_date

app = create_app()

with app.app_context():
    client = app.test_client()

    user = User.query.filter_by(username='admin').first()
    if not user:
        user = User(username='admin', email='admin@admin.com', role='admin')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()

    client.post('/login', data={
        'username': 'admin',
        'password': 'admin123',
        'project': 'belgrad'
    }, follow_redirects=True)

    project = 'belgrad'
    tram_id = '1531'

    # KM: App -> Excel -> API consistency
    client.post('/tramvay-km/guncelle', data={
        'tram_id': tram_id,
        'current_km': '100',
        'notes': 'test sync'
    }, follow_redirects=True)

    eq = Equipment.query.filter_by(equipment_code=tram_id, project_code=project).first()
    km_map = read_all_km(project)
    km_excel = km_map.get(tram_id, {}).get('current_km', None)

    bakim_resp = client.get('/api/bakim-verileri')
    bakim_json = bakim_resp.get_json() if bakim_resp.status_code == 200 else {}
    api_km = None
    for row in bakim_json.get('tramps', []):
        if str(row.get('tram_id')) == tram_id:
            api_km = row.get('current_km')
            break

    print('KM consistency:')
    print(f"  Equipment: {eq.current_km if eq else 'N/A'}")
    print(f"  Excel: {km_excel}")
    print(f"  Bakim API: {api_km}")

    # Service: Excel -> DB sync
    today = datetime.now().strftime('%Y-%m-%d')
    upsert_service_status(
        project_code=project,
        status_date=today,
        tram_id=tram_id,
        status='Servis Dışı',
        sistem='Test Sistem',
        alt_sistem='Test Alt',
        aciklama='Excel->DB test',
        updated_by='external_excel'
    )

    client.get('/servis-durumu')

    db_status = ServiceStatus.query.filter_by(tram_id=tram_id, date=today, project_code=project).first()
    print('Service Excel->DB:')
    print(f"  DB status: {db_status.status if db_status else 'N/A'}")

    # Service: App -> Excel sync
    client.post('/servis-durumu', data={
        'tarih': today,
        'tramvay_id': tram_id,
        'durum': 'Servis',
        'sistem': 'Uygulama Sistem',
        'alt_sistem': 'Uygulama Alt',
        'aciklama': 'DB->Excel test'
    }, follow_redirects=True)

    service_map = read_service_status_by_date(project, today)
    excel_status = service_map.get(tram_id, {}).get('status')
    print('Service App->Excel:')
    print(f"  Excel status: {excel_status}")

    ok = (
        eq is not None and eq.current_km == 100 and km_excel == 100 and api_km == 100
        and db_status is not None and db_status.status in ['Servis Dışı', 'Servis']
        and excel_status == 'Servis'
    )
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'}")
