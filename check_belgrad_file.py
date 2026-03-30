import pandas as pd

belgrad_file = r'logs\belgrad\ariza_listesi\Fracas_BELGRAD.xlsx'

print("Belgrad Fracas sheets:")
try:
    xls = pd.ExcelFile(belgrad_file)
    print(f"  Sheet names: {xls.sheet_names}")
    
    # Try different headers
    for header in [0, 1, 2, 3]:
        try:
            df = pd.read_excel(belgrad_file, sheet_name='FRACAS', header=header)
            print(f"  header={header}: {len(df)} satir - OK")
            break
        except Exception as e:
            print(f"  header={header}: {type(e).__name__}: {str(e)[:50]}")
            
except Exception as e:
    print(f"  Hata: {e}")
