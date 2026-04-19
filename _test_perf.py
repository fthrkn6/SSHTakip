"""Performance test script"""
import time
import json

from app import create_app
app = create_app()

with app.app_context():
    with app.test_client() as client:
        from models import User
        user = User.query.first()
        with client.session_transaction() as sess:
            sess['current_project'] = 'timisoara'
            sess['_user_id'] = str(user.id)
        
        # Time servis-durumu page
        t1 = time.time()
        resp = client.get('/servis-durumu')
        t2 = time.time()
        print(f'servis-durumu: {t2-t1:.2f}s, status={resp.status_code}')
        
        # Time scenarios page
        t1 = time.time()
        resp = client.get('/scenarios')
        t2 = time.time()
        print(f'scenarios: {t2-t1:.2f}s, status={resp.status_code}')
        
        # Time availability trend API - toplam
        t1 = time.time()
        resp = client.get('/scenarios/availability-trend?period=toplam')
        t2 = time.time()
        data = json.loads(resp.data)
        if data.get('success'):
            dates = data['data']['dates']
            avgs = data['data']['averages']
            firstd = dates[0] if dates else 'none'
            lastd = dates[-1] if dates else 'none'
            print(f'avail-trend toplam: {t2-t1:.2f}s, {len(dates)} entries, {firstd} -> {lastd}')
        else:
            print(f'avail-trend toplam: {t2-t1:.2f}s, FAILED: {data}')
        
        # Time scenarios data API - toplam
        t1 = time.time()
        resp = client.get('/scenarios/data?period=toplam')
        t2 = time.time()
        data = json.loads(resp.data)
        print(f'scenarios-data toplam: {t2-t1:.2f}s, status={resp.status_code}')
        
        # Check DB record count for timisoara
        from models import ServiceStatus
        from sqlalchemy import func
        cnt = ServiceStatus.query.filter_by(project_code='timisoara').count()
        mn = ServiceStatus.query.filter_by(project_code='timisoara').with_entities(func.min(ServiceStatus.date)).scalar()
        mx = ServiceStatus.query.filter_by(project_code='timisoara').with_entities(func.max(ServiceStatus.date)).scalar()
        print(f'DB timisoara: {cnt} records, {mn} -> {mx}')
