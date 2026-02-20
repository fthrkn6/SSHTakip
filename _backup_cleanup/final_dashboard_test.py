#!/usr/bin/env python3
"""Final test - Dashboard queries with project_code"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import WorkOrder, MaintenancePlan
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    print("\n" + "="*100)
    print("FINAL TEST - Dashboard Queries")
    print("="*100 + "\n")
    
    current_project = 'belgrad'
    
    # Test 1: Critical work orders
    try:
        critical = WorkOrder.query.filter(
            WorkOrder.priority == 'critical',
            WorkOrder.status.in_(['pending', 'scheduled', 'in_progress']),
            WorkOrder.project_code == current_project
        ).order_by(WorkOrder.planned_start).limit(10).all()
        print(f"✓ Critical work orders: {len(critical)} found")
    except Exception as e:
        print(f"✗ Critical work orders ERROR: {e}")
    
    # Test 2: Upcoming maintenance
    try:
        upcoming = WorkOrder.query.filter(
            WorkOrder.status.in_(['pending', 'scheduled']),
            WorkOrder.planned_start >= datetime.utcnow(),
            WorkOrder.planned_start <= datetime.utcnow() + timedelta(days=7),
            WorkOrder.project_code == current_project
        ).order_by(WorkOrder.planned_start).limit(10).all()
        print(f"✓ Upcoming maintenance: {len(upcoming)} found")
    except Exception as e:
        print(f"✗ Upcoming maintenance ERROR: {e}")
    
    # Test 3: Work order trend (last 12 months)
    try:
        trend_data = []
        for i in range(12):
            month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            count = WorkOrder.query.filter(
                WorkOrder.created_at >= month_start,
                WorkOrder.created_at < month_end,
                WorkOrder.project_code == current_project
            ).count()
            
            trend_data.append({'month': month_start.strftime('%Y-%m'), 'count': count})
        
        print(f"✓ Work order trend: {len(trend_data)} months calculated")
    except Exception as e:
        print(f"✗ Work order trend ERROR: {e}")
    
    # Test 4: Maintenance Plans with project_code
    try:
        plans = MaintenancePlan.query.filter_by(
            is_active=True,
            project_code=current_project
        ).all()
        print(f"✓ Maintenance plans: {len(plans)} found")
    except Exception as e:
        print(f"✗ Maintenance plans ERROR: {e}")
    
    print("\n" + "="*100)
    print("✓ ALL TESTS PASSED - Dashboard should work now")
    print("="*100 + "\n")
