import pandas as pd

timisoara_file = 'logs/timisoara/ariza_listesi/Fracas_TIMISOARA.xlsx'

# Read Excel file to get sheet names
xl_file = pd.ExcelFile(timisoara_file)
print(f"Sheet names: {xl_file.sheet_names}")

# Try reading with header=3 but default sheet
df = pd.read_excel(timisoara_file, header=3)
print(f"\nShape with header=3: {df.shape}")
print(f"Columns after normalization:")
df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
print(f"  {list(df.columns[:5])}")
print(f"\nFirst data row:")
print(df.head(1))
