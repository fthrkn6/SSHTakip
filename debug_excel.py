import pandas as pd
import os

excel_path = os.path.join('data', 'belgrad', 'Veriler.xlsx')

# Tüm sayfaları listele
xls = pd.ExcelFile(excel_path)
print("=== Excel Sayfaları ===")
for i, sheet in enumerate(xls.sheet_names):
    print(f"{i}: {sheet}")

# Sayfa2'yi oku (index 1)
print("\n=== Sayfa2 İçeriği ===")
try:
    df = pd.read_excel(excel_path, sheet_name=1, header=0)
    print(f"Satır sayısı: {len(df)}")
    print(f"Sütunlar: {list(df.columns)}")
    if 'tram_id' in df.columns:
        print(f"\ntram_id değerleri:")
        vals = df['tram_id'].dropna().unique().tolist()[:20]
        print(vals)
    else:
        print("⚠️  tram_id sütunu bulunamadı!")
        print(f"İlk 5 satır:\n{df.head()}")
except Exception as e:
    print(f"Hata: {e}")
