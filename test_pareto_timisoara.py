import pandas as pd
import sys
sys.path.insert(0, '.')
from routes.fracas import calculate_pareto_analysis, get_column

excel_path = 'logs/timisoara/ariza_listesi/Fracas_TIMISOARA.xlsx'
df = pd.read_excel(excel_path, sheet_name='FRACAS', header=3)

# Normalize columns
df.columns = df.columns.str.replace('\n', ' ', regex=False).str.replace('\r', '', regex=False)
df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip()

print(f"VERI: {len(df)} satır")
print()

# Test get_column
module_col = get_column(df, ['araç module', 'vehicle module', 'modül'])
print(f"MODULE KOLONU: {module_col}")

supplier_col = get_column(df, ['tedarikçi', 'supplier', 'relevant supplier'])
print(f"SUPPLIER KOLONU: {supplier_col}")

location_col = get_column(df, ['sistem', 'alt sistem', 'failure location', 'location'])
print(f"LOCATION KOLONU: {location_col}")

class_col = get_column(df, ['arıza sınıfı', 'failure class', 'sınıf', 'failure'])
print(f"CLASS KOLONU: {class_col}")

print()
print("="*50)
print("PARETO ANALIZ ÇALIŞTIRILIYORSONU...")

try:
    pareto = calculate_pareto_analysis(df)
    
    print(f"✓ PARETO TAMAMLANDI")
    print()
    print(f"by_module: {len(pareto['by_module'])} item")
    if pareto['by_module']:
        for item in pareto['by_module'][:3]:
            print(f"  - {item['name']}: {item['count']} arıza")
    
    print()
    print(f"by_supplier: {len(pareto['by_supplier'])} item")
    if pareto['by_supplier']:
        for item in pareto['by_supplier'][:3]:
            print(f"  - {item['name']}: {item['count']} arıza")
    
    print()
    print(f"by_location: {len(pareto['by_location'])} item")
    if pareto['by_location']:
        for item in pareto['by_location'][:3]:
            print(f"  - {item['name']}: {item['count']} arıza")
    
    print()
    print(f"by_failure_class: {len(pareto['by_failure_class'])} item")
    if pareto['by_failure_class']:
        for item in pareto['by_failure_class'][:3]:
            print(f"  - {item['name']}: {item['count']} arıza")
    
except Exception as e:
    print(f"✗ HATA: {e}")
    import traceback
    traceback.print_exc()
