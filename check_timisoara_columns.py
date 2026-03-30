import pandas as pd

excel_path = 'logs/timisoara/ariza_listesi/Fracas_TIMISOARA.xlsx'
df = pd.read_excel(excel_path, sheet_name='FRACAS', header=3)
df.columns = df.columns.str.replace('\n', ' ', regex=False).str.replace('\r', '', regex=False)
df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip()

print("TIMIŞOARA SÜTUNLARI:")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

print("\n" + "="*50)
print("KONTROL EDILECEK SÜTUNLAR:")

# Module
test_names = ['araç module', 'vehicle module', 'modül']
for col in df.columns:
    col_lower = col.lower()
    for name in test_names:
        if name.lower() in col_lower or col_lower in name.lower():
            print(f"✓ MODULE: '{col}'")
            break

# Supplier  
test_names = ['tedarikçi', 'supplier', 'relevant supplier']
for col in df.columns:
    col_lower = col.lower()
    for name in test_names:
        if name.lower() in col_lower or col_lower in name.lower():
            print(f"✓ SUPPLIER: '{col}'")
            break

# Location
test_names = ['sistem', 'alt sistem', 'failure location', 'location']
for col in df.columns:
    col_lower = col.lower()
    for name in test_names:
        if name.lower() in col_lower or col_lower in name.lower():
            print(f"✓ LOCATION: '{col}'")
            break

# Class
test_names = ['arıza sınıfı', 'failure class', 'sınıf', 'failure']
for col in df.columns:
    col_lower = col.lower()
    for name in test_names:
        if name.lower() in col_lower or col_lower in name.lower():
            print(f"✓ CLASS: '{col}'")
            break

# Date
test_names = ['tarih', 'date', 'hata tarih', 'arıza tarihi']
for col in df.columns:
    col_lower = col.lower()
    for name in test_names:
        if name.lower() in col_lower or col_lower in name.lower():
            print(f"✓ DATE: '{col}'")
            break
