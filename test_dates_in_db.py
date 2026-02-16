#!/usr/bin/env python
from app import create_app
from models import ServiceStatus

app = create_app()
with app.app_context():
    all_records = ServiceStatus.query.order_by(ServiceStatus.date).all()
    dates = sorted(set([r.date for r in all_records]))
    
    print(f'All dates in DB:')
    for d in dates:
        count = ServiceStatus.query.filter_by(date=d).count()
        print(f'  {d}: {count} records')
    
    print(f'\nDate range: {min(dates)} to {max(dates)}')
    print(f'Days span: {(max(dates) - min(dates)).days} days')
