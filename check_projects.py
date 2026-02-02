"""Tüm projelerin FRACAS verilerini kontrol et"""
import pandas as pd
import os

projects = ['belgrad', 'iasi', 'timisoara', 'kayseri', 'kocaeli', 'gebze']

print("=" * 60)
print("PROJE FRACAS VERİ KONTROLÜ")
print("=" * 60)

for project in projects:
    project_folder = os.path.join('data', project)
    
    # Excel dosyasını bul
    excel_file = None
    if os.path.exists(project_folder):
        for fn in os.listdir(project_folder):
            if fn.endswith('.xlsx') and not fn.startswith('~$'):
                excel_file = os.path.join(project_folder, fn)
                break
    
    if excel_file:
        try:
            df = pd.read_excel(excel_file, sheet_name='FRACAS', header=3)
            # Sütunları temizle
            df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
            df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
            
            # FRACAS ID kolonunu bul
            fracas_col = None
            for col in df.columns:
                if 'fracas' in col.lower() and 'id' in col.lower():
                    fracas_col = col
                    break
            
            if fracas_col:
                df = df[df[fracas_col].notna()]
            
            # Araç kolonu bul
            vehicle_col = None
            for col in df.columns:
                if 'araç' in col.lower() and 'numar' in col.lower():
                    vehicle_col = col
                    break
            
            vehicle_count = df[vehicle_col].nunique() if vehicle_col else 0
            
            print(f"\n🚋 {project.upper()}")
            print(f"   Dosya: {os.path.basename(excel_file)}")
            print(f"   Kayıt: {len(df)}")
            print(f"   Araç: {vehicle_count}")
            
        except Exception as e:
            print(f"\n❌ {project.upper()}: Hata - {e}")
    else:
        print(f"\n⚠️ {project.upper()}: Excel dosyası bulunamadı")

print("\n" + "=" * 60)
