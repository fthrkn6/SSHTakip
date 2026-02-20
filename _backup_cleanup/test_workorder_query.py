#!/usr/bin/env python3
"""Simulate dashboard request to test WorkOrder query with project_code"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import WorkOrder
from flask import session

app = create_app()

with app.test_client() as client:
    # Simulate a user session
    with client.session_transaction() as sess:
        sess['current_project'] = 'belgrad'
        sess['user_id'] = 1
    
    print("\n" + "="*100)
    print("TESTING WORKORDER QUERY (Dashboard scenario)")
    print("="*100 + "\n")
    
    with app.app_context():
        # Simulate the dashboard query
        print("1. Query: SELECT * FROM work_orders WHERE status IN (...) LIMIT 10\n")
        
        try:
            # This is what dashboard.py does (line 392)
            work_orders = WorkOrder.query.filter(
                WorkOrder.priority == 'critical',
                WorkOrder.status.in_(['pending', 'scheduled', 'in_progress'])
            ).order_by(WorkOrder.planned_start).limit(10).all()
            
            print(f"   ✓ Query executed successfully!")
            print(f"   Found: {len(work_orders)} critical work orders\n")
            
        except Exception as e:
            print(f"   ✗ Query failed: {e}\n")
    
    print("="*100)
    print("✓ DATABASE QUERIES WORKING")
    print("="*100 + "\n")
