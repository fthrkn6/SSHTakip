#!/usr/bin/env python3
"""Activate all projects and populate Equipment/ServiceStatus from Excel files"""
import sys
import os
import pandas as pd
from datetime import date
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment, ServiceStatus

app = create_app()

def load_project_data(project_code):
    """Load and populate data for a project from its Excel files"""
    print(f"\n{'='*80}")
    print(f"📦 Loading {project_code.upper()}")
    print(f"{'='*80}")
    
    # Path to Veriler.xlsx for this project
    excel_path = os.path.join(app.root_path, 'data', project_code, 'Veriler.xlsx')
    
    if not os.path.exists(excel_path):
        print(f"❌ {excel_path} NOT FOUND")
        return
    
    try:
        # Read the tram IDs from Sayfa2
        df = pd.read_excel(excel_path, sheet_name='Sayfa2', header=0)
        print(f"✅ Veriler.xlsx loaded ({len(df)} rows)")
        
        # Get tram_id column (could be named different ways)
        tram_col = None
        for col in ['tram_id', 'equipment_code', 'Tram ID', 'Equipment Code']:
            if col in df.columns:
                tram_col = col
                break
        
        if not tram_col:
            print(f"⚠️  Could not find tram_id column. Available columns: {list(df.columns)}")
            return
        
        tram_ids = df[tram_col].dropna().unique()
        print(f"📍 Found {len(tram_ids)} unique tram IDs")
        
        # Load or create Equipment records
        with app.app_context():
            existing_count = Equipment.query.filter_by(project_code=project_code, parent_id=None).count()
            print(f"   Current Equipment records: {existing_count}")
            
            new_count = 0
            for tram_id in tram_ids:
                tram_id = str(tram_id).strip()
                
                # Check if already exists
                equip = Equipment.query.filter_by(
                    equipment_code=tram_id,
                    project_code=project_code,
                    parent_id=None
                ).first()
                
                if not equip:
                    equip = Equipment(
                        equipment_code=tram_id,
                        name=f"Tramvay {tram_id}",
                        project_code=project_code,
                        parent_id=None,
                        status="aktif",
                        equipment_type="Tram"
                    )
                    db.session.add(equip)
                    new_count += 1
            
            if new_count > 0:
                db.session.commit()
                print(f"   ✅ Added {new_count} new Equipment records")
            
            # Load ServiceStatus records for today
            today = str(date.today())
            ss_count = ServiceStatus.query.filter_by(
                project_code=project_code, 
                date=today
            ).count()
            
            print(f"   Current ServiceStatus records (today): {ss_count}")
            
            # Add sample ServiceStatus records
            new_ss = 0
            for tram_id in tram_ids:
                tram_id = str(tram_id).strip()
                
                existing_ss = ServiceStatus.query.filter_by(
                    tram_id=tram_id,
                    date=today,
                    project_code=project_code
                ).first()
                
                if not existing_ss:
                    # Create with default status
                    status_val = "Servis"  # Default to active
                    
                    ss = ServiceStatus(
                        tram_id=tram_id,
                        date=today,
                        status=status_val,
                        project_code=project_code,
                        system="Ana Sistem",
                        subsystem="Mekanik"
                    )
                    db.session.add(ss)
                    new_ss += 1
            
            if new_ss > 0:
                db.session.commit()
                print(f"   ✅ Added {new_ss} new ServiceStatus records")
            
            # Show final counts
            final_equip = Equipment.query.filter_by(project_code=project_code, parent_id=None).count()
            final_ss = ServiceStatus.query.filter_by(project_code=project_code, date=today).count()
            print(f"\n   📊 Final Count:")
            print(f"      Equipment (trams): {final_equip}")
            print(f"      ServiceStatus (today): {final_ss}")
            
    except Exception as e:
        print(f"❌ Error loading {excel_path}: {str(e)}")

# Main execution
if __name__ == '__main__':
    with app.app_context():
        # Projects to activate
        projects = ['belgrad', 'kayseri', 'iasi', 'timisoara', 'kocaeli', 'gebze']
        
        for project in projects:
            load_project_data(project)
        
        # Show summary
        print(f"\n{'='*80}")
        print("📊 FINAL SUMMARY")
        print(f"{'='*80}\n")
        
        for project in projects:
            equip_count = Equipment.query.filter_by(project_code=project, parent_id=None).count()
            today = str(date.today())
            ss_count = ServiceStatus.query.filter_by(project_code=project, date=today).count()
            print(f"{project.upper():15} → Equipment: {equip_count:3} | ServiceStatus: {ss_count:3}")
        
        print(f"\n{'='*80}\n")
