import pandas as pd

fracas_file = r'data\belgrad\BEL25_FRACAS.xlsx'
df = pd.read_excel(fracas_file, sheet_name='FRACAS', header=0)

# FRACAS ID sütununu bul
fracas_col = None
for col in df.columns:
    if isinstance(col, str) and 'fracas' in col.lower() and 'id' in col.lower():
        fracas_col = col
        break

print(f"FRACAS ID sutunu: '{fracas_col}'")

# ID'leri parse et
ids = []
for val in df[fracas_col].dropna():
    if isinstance(val, str) and 'FF-' in val:
        num = int(val.split('FF-')[-1])
        ids.append(num)

print(f"Toplam ID: {len(ids)}")
print(f"En yeni: {max(ids)}")

# Sonraki ID'yi hesapla
next_id = max(ids) + 1
formatted_id = f"BOZ-BEL25-FF-{next_id:03d}"

print(f"SONUC: {formatted_id}")
