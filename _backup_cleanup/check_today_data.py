import pandas as pd
from datetime import date

excel_file = r'logs\ariza_listesi\Ariza_Listesi_BELGRAD.xlsx'
df = pd.read_excel(excel_file, sheet_name='Ariza Listesi', header=3)

today = date.today()
today_str = today.strftime('%Y-%m-%d')

print(f'Bugünün tarihi: {today_str}')
print(f'Toplam satır: {len(df)}')
print(f'Sütun sayısı: {len(df.columns)}')
print()

if len(df.columns) > 28:
    print(f'Column 5 adı: {df.columns[4]}')
    print(f'Column 29 adı: {df.columns[28]}')
    print()
    
    bugün_satır = []
    kaydedildi_sayı = 0
    
    for idx, row in df.iterrows():
        try:
            tarih = row[df.columns[4]]
            if pd.isna(tarih):
                continue
            
            tarih_str = pd.Timestamp(tarih).strftime('%Y-%m-%d')
            
            if tarih_str == today_str:
                durum = str(row[df.columns[28]]).strip() if not pd.isna(row[df.columns[28]]) else ''
                araç = row[1] if len(row) > 1 else 'N/A'
                print(f'Row {idx}: Araç={araç}, Tarih={tarih_str}, Durum={durum}')
                bugün_satır.append(idx)
                if durum == 'Kaydedildi':
                    kaydedildi_sayı += 1
        except Exception as e:
            pass
            
    print()
    print(f'Bugünün satırları: {len(bugün_satır)}')
    print(f'"Kaydedildi" durumu: {kaydedildi_sayı}')
