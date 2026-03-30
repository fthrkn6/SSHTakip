import pandas as pd

current_project = 'belgrad'
ariza_listesi_file = f'logs/{current_project}/ariza_listesi/Fracas_BELGRAD.xlsx'

df = pd.read_excel(ariza_listesi_file, sheet_name='FRACAS', header=3)

print("=== SÜTUN ARAMA TESTİ ===\n")

# Kod tarafından aranması gereken
sinif_col = None
for col in df.columns:
    if 'arıza' in col.lower() and 'sınıf' in col.lower():
        print(f"BULUNDU: {repr(col)}")
        sinif_col = col
        break

if sinif_col is None:
    print("BULUNAMADI!")
else:
    print(f"\nSütun içeriği (ilk 10):")
    print(df[sinif_col].head(10).to_string())
    
    print(f"\nDeğer counts:")
    print(df[sinif_col].value_counts())
