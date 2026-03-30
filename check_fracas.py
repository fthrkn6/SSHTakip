import pandas as pd
from datetime import datetime, timedelta

# FRACAS dosyasını oku
df = pd.read_excel('logs/belgrad/ariza_listesi/Fracas_BELGRAD.xlsx', 
                    sheet_name='FRACAS', header=3)

print("=== SÜTUNLAR ===")
print(list(df.columns))

print("\n=== TARİH SÜTUNU İLK 10 SATIR ===")
print(df['Hata Tarih/Saat'].head(10))

print(f"\nTarih Sütunu Tipi: {df['Hata Tarih/Saat'].dtype}")

print("\n=== ARIZA SINIFI SÜTUNU ===")
print(df['Arıza Sınıfı\n\n\nFailure Class'].value_counts())

print("\n=== İstatistikler ===")
print(f"Toplam satır: {len(df)}")
print(f"Son 30 gün öncesi tarihi: {datetime.now() - timedelta(days=30)}")

# Tarih filtrelemesi test et
if pd.api.types.is_datetime64_any_dtype(df['Hata Tarih/Saat']):
    last_30_days = datetime.now() - timedelta(days=30)
    filtered = df[df['Hata Tarih/Saat'] >= last_30_days]
    print(f"\nSon 30 günde: {len(filtered)} arıza")
else:
    print("\nTarih sütunu datetime tipinde değil!")
