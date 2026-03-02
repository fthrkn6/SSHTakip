from app import app, db
from models import Equipment
import os
import pandas as pd

with app.app_context():
    # Excel'de 2251 var mı?
    excel_path = 'data/iasi/Veriler.xlsx'
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path, sheet_name='Sayfa2')
        excel_codes = df.iloc[:, 0].dropna().astype(str).str.strip().tolist()
        
        has_2251_excel = '2251' in excel_codes or 2251 in excel_codes
        print(f"Excel'de 2251: {has_2251_excel}")
        print(f"Excel kodları: {sorted([int(float(c)) for c in excel_codes])}")
    else:
        print(f"Excel dosyası bulunamadı")
    
    # Database'de 2251 var mı?
    eq_2251 = Equipment.query.filter_by(equipment_code='2251', project_code='iasi').first()
    
    if eq_2251:
        print(f"\n✗ Database'de 2251 var (silmeli!):")
        print(f"  ID: {eq_2251.id}")
        print(f"  Code: {eq_2251.equipment_code}")
        print(f"  Project: {eq_2251.project_code}")
        
        # Sil
        db.session.delete(eq_2251)
        db.session.commit()
        print(f"✓ 2251 silindi!")
    else:
        print(f"\n✓ Database'de 2251 yok")
