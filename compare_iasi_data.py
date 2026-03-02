import pandas as pd
import os
import json

print("=== İASİ VERİ KARŞILAŞTIRMASI ===\n")

# 1. Excel Sayfa2
excel_path = 'data/iasi/Veriler.xlsx'
if os.path.exists(excel_path):
    df = pd.read_excel(excel_path, sheet_name='Sayfa2')
    excel_codes = df.iloc[:, 0].dropna().astype(str).str.strip().tolist()
    print(f"1. EXCEL SAYFA2: {len(excel_codes)} araç")
    print(f"   Kodlar: {sorted(excel_codes)}")
else:
    print(f"❌ Excel dosyası bulunamadı: {excel_path}")

# 2. Bakım Planları JSON dosyası
bakim_path = 'data/iasi/maintenance.json'
if os.path.exists(bakim_path):
    with open(bakim_path, 'r', encoding='utf-8') as f:
        bakim_data = json.load(f)
    
    if isinstance(bakim_data, dict) and 'plans' in bakim_data:
        bakim_codes = list(bakim_data['plans'].keys())
    else:
        bakim_codes = []
    
    print(f"\n2. BAKIM PLANLARI JSON: {len(bakim_codes)} araç")
    print(f"   Kodlar: {sorted(bakim_codes)}")
else:
    print(f"\n❌ Bakım dosyası bulunamadı: {bakim_path}")

# 3. Karşılaştırma
if excel_codes and bakim_codes:
    excel_set = set(excel_codes)
    bakim_set = set(bakim_codes)
    
    only_in_excel = excel_set - bakim_set
    only_in_bakim = bakim_set - excel_set
    
    print(f"\n3. FARKLARI:")
    if only_in_excel:
        print(f"   ✗ Sadece Excel'de var: {sorted(only_in_excel)}")
    if only_in_bakim:
        print(f"   ✗ Sadece Bakım.json'da var: {sorted(only_in_bakim)}")
    if not only_in_excel and not only_in_bakim:
        print(f"   ✓ Tamamen eşleşiyor!")
