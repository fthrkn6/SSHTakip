import pandas as pd
import os

timisoara_file = 'logs/timisoara/ariza_listesi/Fracas_TIMISOARA.xlsx'

print("Trying different header rows:\n")

for header_row in range(0, 10):
    try:
        df = pd.read_excel(timisoara_file, header=header_row)
        print(f"Header row {header_row}:")
        print(f"  Columns count: {len(df.columns)}")
        print(f"  Shape: {df.shape}")
        valid_cols = [col for col in df.columns if pd.notna(col) and col != '']
        print(f"  Valid columns: {len(valid_cols)}")
        print(f"  First 5 columns: {list(df.columns[:5])}")
        print()
    except Exception as e:
        print(f"Header row {header_row}: Error - {e}\n")

# Try to find actual data row
print("\n" + "="*80)
print("Reading with header=0 to see all rows:")
df = pd.read_excel(timisoara_file, header=0)
print(f"Total rows: {len(df)}")
print(f"\nFirst 10 rows:")
print(df.head(10))
