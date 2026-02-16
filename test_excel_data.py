#!/usr/bin/env python
from app import create_app
from models import ServiceStatus

app = create_app()
with app.app_context():
    # Count records
    total = ServiceStatus.query.count()
    print(f"Total ServiceStatus records: {total}")
    
    # Show a few records
    records = ServiceStatus.query.limit(3).all()
    for r in records:
        print(f"  - {r.tram_id}: {r.date} - {r.status}")
