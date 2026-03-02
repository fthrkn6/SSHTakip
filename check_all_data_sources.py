from app import app
from models import Equipment
import os
import pandas as pd

with app.app_context():
    projects = ['belgrad', 'gebze', 'iasi', 'kayseri', 'kocaeli', 'timisoara']
    
    print("=== TÜM PROJELER: EXCEL vs DATABASE KARŞILAŞTIRMA ===\n")
    
    for proj in projects:
        print(f"\n{proj.upper()}:")
        
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
        
        # Database'den
        db_eq = Equipment.query.filter_by(project_code=proj).all()
        db_codes = set([eq.equipment_code for eq in db_eq])
        db_nums = set()
        for c in db_codes:
            try:
                db_nums.add(int(float(c)))
            except:
                db_nums.add(c)
        
        extra = db_nums - excel_nums
        missing = excel_nums - db_nums
        
        print(f"  Excel: {len(excel_nums)} | Database: {len(db_nums)}")
        if extra:
            print(f"  ✗ Database'de extra (sil): {sorted(list(extra)[:10])}")
        if missing:
            print(f"  ✗ Excel'de ama DB'de yok: {sorted(list(missing)[:10])}")
        if not extra and not missing:
            print(f"  ✓ Perfect match!")
