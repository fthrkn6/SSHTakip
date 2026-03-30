import pandas as pd
from datetime import datetime, timedelta

current_project = 'belgrad'
ariza_listesi_file = f'logs/{current_project}/ariza_listesi/Fracas_BELGRAD.xlsx'

print("=== BELGRAD PROJESİ - FRACAS VERİSİ ===\n")

# Excel'i oku
df = pd.read_excel(ariza_listesi_file, sheet_name='FRACAS', header=3)

print(f"Dosya: {ariza_listesi_file}")
print(f"Toplam satır: {len(df)}\n")

# Tarih sütununu al ve convert et
tarih_col = 'Hata Tarih/Saat'
df[tarih_col] = pd.to_datetime(df[tarih_col], errors='coerce')

print(f"Tarih aralığı:")
print(f"  İlk arıza: {df[tarih_col].min()}")
print(f"  Son arıza: {df[tarih_col].max()}")
print(f"  Bugün: {datetime.utcnow()}")
print(f"  Son 30 gün başlangıcı: {datetime.utcnow() - timedelta(days=30)}\n")

# Son 30 gün filtresi
last_30_days = datetime.utcnow() - timedelta(days=30)
df_filtered = df[df[tarih_col] >= last_30_days].copy()

print(f"Son 30 günde: {len(df_filtered)} arıza\n")

# Sınıf sütununu al
sinif_col = None
for col in df.columns:
    if 'arıza' in col.lower() and 'sınıf' in col.lower():
        sinif_col = col
        break

print(f"Arıza Sınıfı Sütunu: {sinif_col}\n")

# Tüm Excel'deki sınıf dağılımı
print("=== TÜM EXCEL'DE (Tarih filtresi yoksa) ===")
if sinif_col:
    all_counts = {
        'A': 0, 'B': 0, 'C': 0, 'D': 0
    }
    for sinif in df[sinif_col].dropna():
        sinif_str = str(sinif).strip()
        if sinif_str.startswith('A'):
            all_counts['A'] += 1
        elif sinif_str.startswith('B'):
            all_counts['B'] += 1
        elif sinif_str.startswith('C'):
            all_counts['C'] += 1
        elif sinif_str.startswith('D'):
            all_counts['D'] += 1
    
    print("A (Kritik):      ", all_counts['A'])
    print("B (Yüksek):      ", all_counts['B'])
    print("C (Hafif):       ", all_counts['C'])
    print("D (Diğer):       ", all_counts['D'])
    print("TOPLAM:          ", sum(all_counts.values()))

# Son 30 günde sınıf dağılımı
print("\n=== SON 30 GÜNDE (YENİ - TARIFHLI) ===")
if sinif_col:
    filtered_counts = {
        'A': 0, 'B': 0, 'C': 0, 'D': 0
    }
    for sinif in df_filtered[sinif_col].dropna():
        sinif_str = str(sinif).strip()
        if sinif_str.startswith('A'):
            filtered_counts['A'] += 1
        elif sinif_str.startswith('B'):
            filtered_counts['B'] += 1
        elif sinif_str.startswith('C'):
            filtered_counts['C'] += 1
        elif sinif_str.startswith('D'):
            filtered_counts['D'] += 1
    
    print("A (Kritik):      ", filtered_counts['A'])
    print("B (Yüksek):      ", filtered_counts['B'])
    print("C (Hafif):       ", filtered_counts['C'])
    print("D (Diğer):       ", filtered_counts['D'])
    print("TOPLAM:          ", sum(filtered_counts.values()))

print("\n=== SON 30 GÜN DETAYı ===")
print(df_filtered[['FRACAS ID', tarih_col, 'Arıza Sınıfı\n\n\nFailure Class']].to_string())
