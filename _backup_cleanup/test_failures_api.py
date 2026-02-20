"""API endpoint sonucunu test et"""
import pandas as pd

excel_path = 'data/belgrad/Veriler.xlsx'
df = pd.read_excel(excel_path, sheet_name='Sayfa2', header=0)

print('TEST: API /api/failures/1553 endpoint\'i ne dönecek?')
print('='*60)

# Araç 1553'ü sor
equipment_code = '1553'
eq_clean = str(equipment_code).strip()
filtered_df = df[df['tram_id'].astype(str) == eq_clean]

if len(filtered_df) > 0:
    row = filtered_df.iloc[0]
    print(f'✓ Araç {equipment_code} bulundu:')
    print(f'  Sistem: {row.get("Module", "")}')
    print(f'  Arıza Sınıfı: {row["Arıza Sınıfı "]}')
    print(f'  Arıza Kaynağı: {row["Arıza Kaynağı"]}')
    print(f'  Arıza Tipi: {row.get("Arıza Tipi", "")}')
else:
    print(f'✗ Araç {equipment_code} bulunamadı')

print('\n' + '='*60)
print('Son 5 araçta arızalar (1553-1557):')
print('='*60)

last_5 = df.tail(5)
for idx, row in last_5.iterrows():
    tram_id = int(row['tram_id'])
    ariza = row['Arıza Sınıfı '] if pd.notna(row['Arıza Sınıfı ']) else 'Yok'
    print(f'{tram_id}: {ariza}')

print('\n✓ Fleet açıldığında tüm son 5 araçta arızalar gösterilecek')
