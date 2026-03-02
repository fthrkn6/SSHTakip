from app import app, db
from models import Equipment
import os
import pandas as pd

with app.app_context():
    # Check if 2001-2017 exists in Database
    equipment_2001 = Equipment.query.filter(Equipment.equipment_code.like('200%')).all()
    equipment_2017 = Equipment.query.filter(Equipment.equipment_code == '2017').all()
    
    print("=== DATABASE KONTROLÜ ===")
    print(f"200x araçlar: {len(equipment_2001)} adet")
    if equipment_2001:
        for eq in equipment_2001:
            print(f"  {eq.equipment_code} -> project: {eq.project_code}")
    
    print(f"\n2017 araç: {len(equipment_2017)} adet")
    if equipment_2017:
        for eq in equipment_2017:
            print(f"  {eq.equipment_code} -> project: {eq.project_code}")
    
    # Check all projects' Excel files
    print("\n\n=== EXCEL KONTROLÜ ===")
    projects = ['belgrad', 'gebze', 'iasi', 'kayseri', 'kocaeli', 'timisoara']
    
    for proj in projects:
        excel_path = f'data/{proj}/Veriler.xlsx'
        if os.path.exists(excel_path):
            try:
                df = pd.read_excel(excel_path, sheet_name='Sayfa2')
                codes = df.iloc[:, 0].dropna().astype(str).tolist()
                
                # Check if any 200x codes
                matches = [c for c in codes if str(c).startswith('200') or c == '2017']
                
                if matches:
                    print(f"✓ {proj}: Bulundu: {matches}")
                else:
                    print(f"✗ {proj}: 2001-2017 yok")
            except Exception as e:
                print(f"✗ {proj}: Hata - {e}")
        else:
            print(f"✗ {proj}: Dosya yok")
