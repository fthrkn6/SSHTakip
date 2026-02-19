import openpyxl

excel_file = 'data/belgrad/Belgrad-Bakım.xlsx'
wb = openpyxl.load_workbook(excel_file)
sheets = wb.sheetnames

print("Excel'deki Sekmeler:")
for i, sheet in enumerate(sheets, 1):
    print(f"  {i}. {sheet}")

print("\n✅ Gerekli sekmeleri kontrol et:")
required = ['6K', '18K', '24K', '36K', '60K', '72K', '102K', '138K', '144K', '204K', '210K', '216K', '276K', '300K']
missing = [s for s in required if s not in sheets]
if missing:
    print(f"❌ Eksik sekmeler: {missing}")
else:
    print("✅ Tüm sekmeler mevcut!")
