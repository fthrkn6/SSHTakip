import pandas as pd

excel_file = r'logs\ariza_listesi\Ariza_Listesi_BELGRAD.xlsx'

# Dosyayı oku - header=3 (Row 4)
df = pd.read_excel(excel_file, sheet_name='Ariza Listesi', header=3)

print('Okunmuş veri:')
print(df.head())
print(f'\nSütunlar: {list(df.columns)}')
print(f'\nPersonel Sayısı sütunu index: {list(df.columns).index("Personel Sayısı")}')

# Personel sayılarını ekle
personel_sayilari = [2, 1, 3, 2, 1, 2, 1, 3]

print('\n' + '='*50)
print('Personel Sayılarını Ekleniyor:')
print('='*50)

for idx, personel in enumerate(personel_sayilari):
    df.iloc[idx, df.columns.get_loc('Personel Sayısı')] = personel
    print(f'Row {idx}: {df.iloc[idx, 1]} -> Personel Sayısı={personel}')

# Excel'e yaz
df.to_excel(excel_file, sheet_name='Ariza Listesi', header=True, startrow=3, index=False)

print('\n✅ Veriler kaydedildi!')
