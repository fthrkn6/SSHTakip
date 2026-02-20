import pandas as pd
import os
import json

# Simulate the endpoint logic
current_project = 'belgrad'
veriler_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', current_project, 'Veriler.xlsx')

print(f"Reading from: {veriler_file}")
print(f"File exists: {os.path.exists(veriler_file)}")

df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
print(f"\nTotal rows: {len(df)}")

# No equipment_code - get last 5
filtered_df = df.tail(5)
print(f"\nLast 5 rows:")
print(filtered_df[['tram_id', 'Module', 'Arıza Sınıfı ', 'Arıza Kaynağı', 'Arıza Tipi']].to_string())

# Process like API does
failures = []
for idx, row in filtered_df.iterrows():
    tram_id = str(row.get('tram_id', '')).strip()
    module = str(row.get('Module', '')).strip()
    ariza_sinifi = str(row.get('Arıza Sınıfı ', '')).strip()
    ariza_kaynagi = str(row.get('Arıza Kaynağı', '')).strip()
    ariza_tipi = str(row.get('Arıza Tipi', '')).strip()
    
    print(f"\nProcessing row {tram_id}:")
    print(f"  ariza_sinifi: '{ariza_sinifi}'")
    print(f"  ariza_kaynagi: '{ariza_kaynagi}'")
    print(f"  ariza_tipi: '{ariza_tipi}'")
    
    if ariza_sinifi == 'nan' or not ariza_sinifi:
        print(f"  -> SKIPPED (ariza_sinifi is nan or empty)")
        continue
    
    failures.append({
        'fracas_id': tram_id,
        'arac_no': tram_id,
        'sistem': module,
        'ariza_tanimi': ariza_sinifi,
        'tarih': '',
        'durum': f'{ariza_kaynagi} | {ariza_tipi}' if ariza_kaynagi else ariza_tipi
    })
    print(f"  -> ADDED")

print(f"\n\nTotal failures returned: {len(failures)}")
print("\nFailures JSON:")
for f in failures:
    print(json.dumps(f, ensure_ascii=False, indent=2))

# Also test with specific vehicle code
print("\n\n" + "="*60)
print("Testing with equipment_code=1553")
print("="*60)

equipment_code = '1553'
eq_clean = str(equipment_code).strip()
filtered_df = df[df['tram_id'].astype(str) == eq_clean]
print(f"\nFiltered rows for {equipment_code}: {len(filtered_df)}")
print(filtered_df[['tram_id', 'Module', 'Arıza Sınıfı ', 'Arıza Kaynağı', 'Arıza Tipi']].to_string())

failures = []
for idx, row in filtered_df.iterrows():
    tram_id = str(row.get('tram_id', '')).strip()
    module = str(row.get('Module', '')).strip()
    ariza_sinifi = str(row.get('Arıza Sınıfı ', '')).strip()
    ariza_kaynagi = str(row.get('Arıza Kaynağı', '')).strip()
    ariza_tipi = str(row.get('Arıza Tipi', '')).strip()
    
    if ariza_sinifi == 'nan' or not ariza_sinifi:
        continue
    
    failures.append({
        'fracas_id': tram_id,
        'arac_no': tram_id,
        'sistem': module,
        'ariza_tanimi': ariza_sinifi,
        'tarih': '',
        'durum': f'{ariza_kaynagi} | {ariza_tipi}' if ariza_kaynagi else ariza_tipi
    })

print(f"\nFailures for {equipment_code}: {len(failures)}")
for f in failures:
    print(json.dumps(f, ensure_ascii=False, indent=2))
