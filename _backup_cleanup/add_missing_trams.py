"""1556-1557 araçlarını Excel'e ekle"""
import pandas as pd

excel_path = 'data/belgrad/Veriler.xlsx'
df = pd.read_excel(excel_path, sheet_name='Sayfa2', header=0)

print(f'Mevcut satırlar: {len(df)}')

# 1556-1557 ekle
new_rows = [
    {
        'tram_id': 1556,
        'Project': 'BEL25',
        'Module': 'EM',
        'Arıza Sınıfı ': 'B-Yüksek/Operasyon Engeller',
        'Arıza Kaynağı': 'Tedarikçi',
        'Arıza Tipi': '(III) Farklı Araçlarda Tekrarlayan Arıza'
    },
    {
        'tram_id': 1557,
        'Project': 'BEL25',
        'Module': 'SYS',
        'Arıza Sınıfı ': 'C-Hafif/Kısıtlı Operasyon',
        'Arıza Kaynağı': 'Bozankaya',
        'Arıza Tipi': '(II) Aynı Araçta Tekrarlayan Arıza'
    }
]

df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

print(f'Yeni satır sayısı: {len(df)}')
print(f'\nSon 3 araç:')
print(df[['tram_id', 'Arıza Sınıfı ', 'Arıza Kaynağı']].tail(3).to_string(index=False))

# Kaydet
df.to_excel(excel_path, sheet_name='Sayfa2', index=False)
print(f'\n✓ 1556-1557 eklendi')
