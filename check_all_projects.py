import pandas as pd
from datetime import datetime, timedelta
import os

projects = ['belgrad', 'gebze', 'istanbul', 'kayseri', 'kocaeli', 'samsun', 'timisoara', 'iasi']

print("=== TÜM PROJELER - SON 30 GÜN ARIZA SAYıLARI ===\n")

for project in projects:
    ariza_dir = f'logs/{project}/ariza_listesi'
    
    if not os.path.exists(ariza_dir):
        print(f"{project.upper():15} → Klasör yok")
        continue
    
    # FRACAS dosyasını bul
    fracas_file = None
    for file in os.listdir(ariza_dir):
        if 'fracas' in file.lower() and file.endswith('.xlsx'):
            fracas_file = os.path.join(ariza_dir, file)
            break
    
    if not fracas_file:
        print(f"{project.upper():15} → FRACAS dosyası yok")
        continue
    
    try:
        # Excel oku
        df = pd.read_excel(fracas_file, sheet_name='FRACAS', header=3)
        
        # Tarih filtresi
        tarih_col = None
        for col in df.columns:
            if 'tarih' in col.lower() and 'hata' in col.lower():
                tarih_col = col
                break
        
        if tarih_col:
            df[tarih_col] = pd.to_datetime(df[tarih_col], errors='coerce')
            last_30_days = datetime.utcnow() - timedelta(days=30)
            df_filtered = df[df[tarih_col] >= last_30_days]
        else:
            df_filtered = df
        
        # Sınıf sütunu
        sinif_col = None
        for col in df.columns:
            if 'arıza' in col.lower() and 'sınıf' in col.lower():
                sinif_col = col
                break
        
        # Sınıflara göre say
        if sinif_col:
            counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
            for sinif in df_filtered[sinif_col].dropna():
                sinif_str = str(sinif).strip()
                if sinif_str.startswith('A'):
                    counts['A'] += 1
                elif sinif_str.startswith('B'):
                    counts['B'] += 1
                elif sinif_str.startswith('C'):
                    counts['C'] += 1
                elif sinif_str.startswith('D'):
                    counts['D'] += 1
            
            total = sum(counts.values())
            print(f"{project.upper():15} → A:{counts['A']:2d}  B:{counts['B']:2d}  C:{counts['C']:2d}  D:{counts['D']:2d}  TOPLAM:{total:2d}")
        else:
            print(f"{project.upper():15} → Sınıf sütunu yok")
    
    except Exception as e:
        print(f"{project.upper():15} → Hata: {e}")

print("\n\n=== HANGI PROJEDE ÇALIŞIYORSUNUZ? ===")
