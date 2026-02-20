#!/usr/bin/env python3
"""Check actual database records"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import ServiceStatus
from datetime import date

app = create_app()
with app.app_context():
    today_date = str(date.today())
    
    print("\n" + "="*70)
    print(f"DATABASE CHECK - Date: {today_date}")
    print("="*70 + "\n")
    
    # BELGRAD
    belgrad_records = ServiceStatus.query.filter_by(
        project_code='belgrad',
        date=today_date
    ).order_by(ServiceStatus.tram_id).all()
    
    print(f"BELGRAD - Total records: {len(belgrad_records)}\n")
    
    status_counts = {}
    for rec in belgrad_records:
        status = rec.status
        status_counts[status] = status_counts.get(status, 0) + 1
        print(f"  {rec.tram_id}: {rec.status}")
    
    print(f"\nStatus breakdown for BELGRAD:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    
    print("\n" + "="*70 + "\n")
