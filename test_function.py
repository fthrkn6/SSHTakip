import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# Flask context olmadan doğrudan test et
class MockSession(dict):
    def get(self, key, default=None):
        return default

# Session mock'u
class GlobalSession:
    session = {'current_project': 'belgrad'}
    
session = GlobalSession.session

class ProjectManager:
    @staticmethod
    def get_fracas_file(project_code):
        from flask import Flask
        app = Flask(__name__)
        ariza_dir = os.path.join(app.root_path if hasattr(app, 'root_path') else '.', 'logs', project_code, 'ariza_listesi')
        
        # Dosyayı bul
        if os.path.exists(ariza_dir):
            for file in os.listdir(ariza_dir):
                if 'fracas' in file.lower() and file.endswith('.xlsx'):
                    return os.path.join(ariza_dir, file)
        
        return None

def get_ariza_counts_by_class():
    """Excel'den arızaları sınıflara göre say (A, B, C, D) - Proje-dinamik"""
    
    current_project = session.get('current_project', 'belgrad')
    ariza_dir = os.path.join('logs', current_project, 'ariza_listesi')
    
    # FRACAS dosyasını bul
    ariza_listesi_file = ProjectManager.get_fracas_file(current_project)
    
    # Başlangıçta tüm sınıfları 0 ile init et
    counts = {
        'A': {'label': 'A-Kritik/Emniyet Riski', 'count': 0},
        'B': {'label': 'B-Yüksek/Operasyon Engeller', 'count': 0},
        'C': {'label': 'C-Hafif/Kısıtlı Operasyon', 'count': 0},
        'D': {'label': 'D-Arıza Değildir', 'count': 0}
    }
    
    if not ariza_listesi_file:
        print(f'FRACAS dosyası bulunamadı')
        return counts
    
    print(f'FRACAS dosyası: {os.path.basename(ariza_listesi_file)}')
    
    try:
        # Header row'u belirle - logs klasöründe ise 3, yoksa 0
        header_row = 3 if 'logs' in ariza_listesi_file and 'ariza_listesi' in ariza_listesi_file else 0
        df = pd.read_excel(ariza_listesi_file, sheet_name='FRACAS', header=header_row)
        
        print(f'DataFrame boyutu (filtresiz): {len(df)} satır')
        
        # SON 30 GÜNDE ARIZALARI FİLTRELE
        # Tarih sütununu bul
        tarih_col = None
        for col in df.columns:
            if 'tarih' in col.lower() and 'hata' in col.lower():
                tarih_col = col
                break
        
        print(f'Tarih sütunu bulundu: {tarih_col}')
        
        # Tarih sütununu datetime'a dönüştür
        if tarih_col:
            try:
                df[tarih_col] = pd.to_datetime(df[tarih_col], errors='coerce')
                # Son 30 gün öncesinden sonraki arızaları filtrele
                last_30_days = datetime.utcnow() - timedelta(days=30)
                print(f'Tarih filtresi uygulanıyor: {tarih_col} >= {last_30_days}')
                df = df[df[tarih_col] >= last_30_days]
                print(f'Filtrelenmiş DataFrame: {len(df)} satır')
            except Exception as e:
                print(f'Tarih dönüşüm hatası: {e}. Tüm arızalar sayılacak.')
        else:
            print(f'Tarih sütunu bulunamadı!')
        
        # Arıza sınıfı sütununu bul
        sinif_col = None
        for col in df.columns:
            if 'arıza' in col.lower() and 'sınıf' in col.lower():
                sinif_col = col
                break
        
        print(f'Arıza sınıfı sütunu bulundu: {sinif_col}')
        
        if sinif_col:
            # Her arızayı kategorize et
            for sinif in df[sinif_col].dropna():
                sinif_str = str(sinif).strip()
                
                # Sınıfın ilk harfini al (A, B, C, D)
                if sinif_str.startswith('A'):
                    counts['A']['count'] += 1
                elif sinif_str.startswith('B'):
                    counts['B']['count'] += 1
                elif sinif_str.startswith('C'):
                    counts['C']['count'] += 1
                elif sinif_str.startswith('D'):
                    counts['D']['count'] += 1
            
            print(f'Ariza sınıfı sayıları (son 30 gün): {counts}')
        else:
            print(f'Ariza sınıfı sütunu bulunamadı!')
        
        return counts
    except Exception as e:
        print(f'Ariza sinifi hesaplama hatasi: {e}')
        import traceback
        print(traceback.format_exc())
        return counts

# Test et
print("=== get_ariza_counts_by_class() TEST ===\n")
result = get_ariza_counts_by_class()

print("\n=== SONUÇ ===")
print(f"A: {result['A']['count']}")
print(f"B: {result['B']['count']}")
print(f"C: {result['C']['count']}")
print(f"D: {result['D']['count']}")
print(f"Toplam: {sum(r['count'] for r in result.values())}")
