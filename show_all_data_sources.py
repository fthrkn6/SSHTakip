#!/usr/bin/env python3
"""Complete data inventory for all projects"""
import sys
import os
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment, ServiceStatus, WorkOrder, Failure, RootCauseAnalysis
from datetime import date, timedelta
import pandas as pd

app = create_app()
with app.app_context():
    today = str(date.today())
    
    print("\n" + "="*100)
    print("📊 COMPLETE DATA INVENTORY - ALL PROJECTS & DATA SOURCES")
    print("="*100)
    
    # Define all projects
    all_projects = ['belgrad', 'kayseri', 'iasi', 'timisoara', 'kocaeli', 'gebze']
    
    print("\n1️⃣  TRAM DATA SOURCES (Araç Envanteri)")
    print("-" * 100)
    
    for project in all_projects:
        print(f"\n{project.upper()}:")
        
        # Check Veriler.xlsx
        veriler_path = os.path.join(app.root_path, 'data', project, 'Veriler.xlsx')
        excel_count = 0
        excel_status = "❌ NOT FOUND"
        
        if os.path.exists(veriler_path):
            try:
                df = pd.read_excel(veriler_path, sheet_name='Sayfa2', header=0)
                if 'tram_id' in df.columns or 'equipment_code' in df.columns:
                    col_name = 'tram_id' if 'tram_id' in df.columns else 'equipment_code'
                    excel_count = len(df[col_name].dropna().unique())
                    excel_status = f"✅ EXISTS ({excel_count} trams)"
            except Exception as e:
                excel_status = f"⚠️  EXISTS but error: {str(e)[:40]}"
        
        # Check Equipment table
        equip_count = Equipment.query.filter_by(project_code=project, parent_id=None).count()
        equip_status = f"✅ {equip_count} records" if equip_count > 0 else "⚠️  0 records"
        
        # Check ServiceStatus table
        ss_count = ServiceStatus.query.filter_by(project_code=project).count()
        ss_today = ServiceStatus.query.filter_by(project_code=project, date=today).count()
        
        print(f"  📁 Veriler.xlsx (Sayfa2): {excel_status}")
        print(f"  🗄️  Equipment table: {equip_status}")
        print(f"  📋 ServiceStatus table: {ss_count} total | {ss_today} today")
        
        if equip_count > 0:
            sample_trams = Equipment.query.filter_by(project_code=project, parent_id=None).limit(3).all()
            print(f"     Sample trams: {', '.join([e.equipment_code for e in sample_trams])}...")
    
    print("\n" + "="*100)
    print("2️⃣  EQUIPMENT DATA DETAILS")
    print("-" * 100)
    
    total_equipment = 0
    for project in all_projects:
        count = Equipment.query.filter_by(project_code=project, parent_id=None).count()
        total_equipment += count
        print(f"{project.upper():15} → {count:3} araç")
    
    print(f"{'TOTAL':15} → {total_equipment:3} araç")
    
    print("\n" + "="*100)
    print("3️⃣  SERVICE STATUS DATA (Günlük Durum Kayıtları)")
    print("-" * 100)
    
    total_ss = 0
    for project in all_projects:
        count = ServiceStatus.query.filter_by(project_code=project).count()
        today_count = ServiceStatus.query.filter_by(project_code=project, date=today).count()
        total_ss += count
        print(f"{project.upper():15} → Total: {count:5} | Today: {today_count:3}")
    
    print(f"{'TOTAL':15} → Total: {total_ss:5}")
    
    print("\n" + "="*100)
    print("4️⃣  FAILURE DATA (Arıza Kayıtları)")
    print("-" * 100)
    
    # Check Excel files for failure data
    for project in all_projects:
        ariza_path = os.path.join(app.root_path, 'data', project, 'ARIZALAR.xlsx')
        
        if os.path.exists(ariza_path):
            try:
                df = pd.read_excel(ariza_path)
                count = len(df)
                print(f"{project.upper():15} → {count} arıza kaydı (ARIZALAR.xlsx)")
            except:
                print(f"{project.upper():15} → ARIZALAR.xlsx exists but error reading")
        else:
            print(f"{project.upper():15} → ❌ ARIZALAR.xlsx NOT FOUND")
    
    print("\n" + "="*100)
    print("5️⃣  MAINTENANCE DATA (Bakım İş Emirleri)")
    print("-" * 100)
    
    for project in all_projects:
        wo_count = WorkOrder.query.filter_by(project_code=project).count() if hasattr(WorkOrder, 'project_code') else 0
        print(f"{project.upper():15} → WorkOrder tablosu: {wo_count} records")
    
    print("\n" + "="*100)
    print("6️⃣  DATA MAPPING IN ROUTES")
    print("-" * 100)
    
    data_sources = {
        "Dashboard Page": [
            "Equipment.query (tram list) - filtered by project_code",
            "ServiceStatus.query (daily status) - filtered by project_code, date=today",
            "Veriler.xlsx (tram_id list) - data/{project}/Veriler.xlsx Sayfa2",
            "AvailabilityMetrics - MTTR calculation"
        ],
        "Service Status Page": [
            "Equipment.query - filtered by project_code",
            "ServiceStatus.query - filtered by project_code, date=today",
            "AvailabilityMetrics - availability percentage",
            "get_tram_ids_from_veriler() - Veriler.xlsx Sayfa2"
        ],
        "Failure/Arıza Pages": [
            "Excel files: data/{project}/ARIZALAR.xlsx",
            "Failure model (database fallback)",
            "RootCauseAnalysis (RCA data)"
        ],
        "Maintenance Pages": [
            "WorkOrder model (filtered by project_code)",
            "MaintenancePlan model",
            "AvailabilityMetrics"
        ]
    }
    
    for page, sources in data_sources.items():
        print(f"\n{page}:")
        for i, source in enumerate(sources, 1):
            print(f"  {i}. {source}")
    
    print("\n" + "="*100)
    print("7️⃣  FILE STRUCTURE")
    print("-" * 100)
    
    print("\nProject data directory structure:")
    for project in all_projects:
        data_dir = os.path.join(app.root_path, 'data', project)
        print(f"\ndata/{project}/")
        
        if os.path.exists(data_dir):
            files = os.listdir(data_dir)
            for f in sorted(files):
                fpath = os.path.join(data_dir, f)
                if os.path.isfile(fpath):
                    size = os.path.getsize(fpath)
                    size_str = f"{size/1024:.1f}KB" if size > 1024 else f"{size}B"
                    print(f"  📄 {f:30} ({size_str})")
        else:
            print(f"  ❌ Directory not found")
    
    print("\n" + "="*100)
    print("8️⃣  DATA ISOLATION VERIFICATION")
    print("-" * 100)
    
    # Check for cross-project contamination
    print("\nChecking if data is properly isolated by project_code:\n")
    
    for project in all_projects:
        equip = Equipment.query.filter_by(project_code=project).count()
        other_equip = Equipment.query.filter(
            Equipment.project_code != project
        ).count()
        
        ss = ServiceStatus.query.filter_by(project_code=project).count()
        other_ss = ServiceStatus.query.filter(
            ServiceStatus.project_code != project
        ).count()
        
        print(f"{project.upper():15} → Equip: {equip:3} (others: {other_equip:3}) | SS: {ss:5} (others: {other_ss:5})")
    
    print("\n" + "="*100 + "\n")
