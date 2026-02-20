#!/usr/bin/env python3
"""Verify project data isolation is working"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment, ServiceStatus
from datetime import datetime

app = create_app()
with app.app_context():
    today = datetime.now().date()
    
    print("\n" + "="*70)
    print("PROJECT DATA ISOLATION VERIFICATION")
    print("="*70)
    
    # Check Equipment table by project
    print("\n1. EQUIPMENT TABLE (Real tram_id's from Veriler.xlsx):")
    print("-" * 70)
    
    for project in ['belgrad', 'kayseri']:
        equipment = Equipment.query.filter_by(project_code=project).all()
        codes = sorted([e.equipment_code for e in equipment])
        print(f"\n  {project.upper()}:")
        print(f"    Count: {len(equipment)}")
        if codes:
            print(f"    Range: {codes[0]} - {codes[-1]}")
            print(f"    All: {codes}")
    
    # Check ServiceStatus by project for today
    print("\n\n2. SERVICE STATUS TABLE (Today's statuses):")
    print("-" * 70)
    
    for project in ['belgrad', 'kayseri']:
        statuses = ServiceStatus.query.filter_by(
            project_code=project, 
            date=today
        ).all()
        print(f"\n  {project.upper()}:")
        print(f"    Records: {len(statuses)}")
        if statuses:
            status_counts = {}
            for s in statuses:
                status = s.status
                status_counts[status] = status_counts.get(status, 0) + 1
            print(f"    Status breakdown: {status_counts}")
    
    # Verify isolation - cross-project contamination check
    print("\n\n3. ISOLATION CHECK:")
    print("-" * 70)
    
    belgrad_equip = [e.equipment_code for e in Equipment.query.filter_by(project_code='belgrad').all()]
    kayseri_equip = [e.equipment_code for e in Equipment.query.filter_by(project_code='kayseri').all()]
    
    overlap = set(belgrad_equip) & set(kayseri_equip)
    
    if overlap:
        print(f"  ❌ CONTAMINATION DETECTED: {overlap}")
    else:
        print(f"  ✅ No cross-project contamination")
    
    # Test query isolation
    print("\n\n4. QUERY ISOLATION TEST:")
    print("-" * 70)
    
    print("\n  Testing: ServiceStatus filter by project_code")
    for project in ['belgrad', 'kayseri']:
        service_count = ServiceStatus.query.filter_by(
            project_code=project,
            date=today
        ).count()
        equip_count = Equipment.query.filter_by(project_code=project).count()
        match = "✅" if service_count == equip_count else "❌"
        print(f"    {project}: Equipment={equip_count}, ServiceStatus today={service_count} {match}")
    
    print("\n" + "="*70)
    print("VERIFICATION COMPLETE")
    print("="*70 + "\n")
