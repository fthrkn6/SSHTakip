#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from app import create_app
from models import ServiceStatus

app = create_app()

with app.app_context():
    all_records = ServiceStatus.query.all()
    
    print("Tum Kayitlar:")
    for rec in all_records:
        print(f"  {rec.date} | {rec.tram_id} | Status: '{rec.status}' | {rec.sistem}")
    
    print("\n\nStatus Degerleri:")
    statuses = set(r.status for r in all_records)
    for s in statuses:
        count = len([r for r in all_records if r.status == s])
        print(f"  Status '{s}': {count} kayit")
