import pandas as pd
from datetime import datetime, timedelta

df = pd.read_excel('logs/timisoara/ariza_listesi/Fracas_TIMISOARA.xlsx', sheet_name='FRACAS', header=3)
tarih_col = 'Hata Tarih/Saat'

print('=== TIMIŞOARA TARİH FİLTRESİ ===')
print(f'Toplam satır: {len(df)}')

df[tarih_col] = pd.to_datetime(df[tarih_col], errors='coerce')
print(f'Min tarih: {df[tarih_col].min()}')
print(f'Max tarih: {df[tarih_col].max()}')

last_30_days = datetime.utcnow() - timedelta(days=30)
print(f'Bugün: {datetime.utcnow()}')
print(f'Son 30 gün başlangıcı: {last_30_days}')

df_filtered = df[df[tarih_col] >= last_30_days]
print(f'\nSon 30 günde: {len(df_filtered)} satır')

sinif_col = 'Arıza Sınıfı\n\n\nFailure Class'
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

print(f'\nSon 30 gündeki sınıf dağılımı:')
print(f"A: {counts['A']}")
print(f"B: {counts['B']}")
print(f"C: {counts['C']}")
print(f"D: {counts['D']}")
print(f"TOPLAM: {sum(counts.values())}")

print(f"\n\n=== TÜM EXCEL'DE (FILTRE YOK) ===")
counts_all = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
for sinif in df[sinif_col].dropna():
    sinif_str = str(sinif).strip()
    if sinif_str.startswith('A'):
        counts_all['A'] += 1
    elif sinif_str.startswith('B'):
        counts_all['B'] += 1
    elif sinif_str.startswith('C'):
        counts_all['C'] += 1
    elif sinif_str.startswith('D'):
        counts_all['D'] += 1

print(f"A: {counts_all['A']}")
print(f"B: {counts_all['B']}")
print(f"C: {counts_all['C']}")
print(f"D: {counts_all['D']}")
print(f"TOPLAM: {sum(counts_all.values())}")
