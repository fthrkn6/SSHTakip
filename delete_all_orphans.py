from app import app, db
from models import Equipment
import os
import pandas as pd

with app.app_context():
    projects = ['belgrad', 'gebze', 'iasi', 'kayseri', 'kocaeli', 'timisoara']
    
    total_deleted = 0
    
    print("=== ORPHAN ARAÇLAR SİLİNİYOR ===\n")
    
    for proj in projects:
        # Excel'den
        excel_path = f'data/{proj}/Veriler.xlsx'
        if os.path.exists(excel_path):
            df = pd.read_excel(excel_path, sheet_name='Sayfa2')
            excel_codes = set(df.iloc[:, 0].dropna().astype(str).str.strip().tolist())
            # Numeric codes
            excel_nums = set()
            for c in excel_codes:
                try:
                    excel_nums.add(int(float(c)))
                except:
                    excel_nums.add(c)
        else:
            excel_nums = set()
        
        # Database'den - TÜM equipment'ler (parent_id=None veya hepsi)
        db_eq = Equipment.query.filter_by(project_code=proj).all()
        db_codes = [eq.equipment_code for eq in db_eq]
        
        # Silinecekleri bul (DB'de var ama Excel'de yok)
        to_delete = []
        for eq in db_eq:
            try:
                eq_num = int(float(eq.equipment_code))
            except:
                eq_num = eq.equipment_code
            
            if eq_num not in excel_nums:
                to_delete.append(eq)
        
        if to_delete:
            print(f"{proj.upper()}: {len(to_delete)} orphan siliyor...")
            for eq in to_delete:
                print(f"  - {eq.equipment_code}")
                db.session.delete(eq)
            total_deleted += len(to_delete)
        else:
            print(f"{proj.upper()}: Temiz ✓")
    
    db.session.commit()
    print(f"\n✓ Toplam {total_deleted} orphan araç silindi!")
