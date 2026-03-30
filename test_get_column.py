import pandas as pd

df = pd.read_excel('logs/timisoara/ariza_listesi/Fracas_TIMISOARA.xlsx', header=3)
print(f"Original columns before normalization:")
print(f"  {list(df.columns[:5])}")

# Normalize columns (as done in load_fracas_data)
df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
print(f"\nNormalized columns:")
print(f"  {list(df.columns[:5])}")
print(f"  All columns: {list(df.columns)}")

# Test get_column function
def get_column(df, possible_names):
    """Olası kolon isimlerinden birini bul - tam ve kısmi eşleştirme"""
    # Önce tam eşleştirme dene
    for col in df.columns:
        col_clean = col.strip().lower()
        for name in possible_names:
            if name.lower() == col_clean:
                return col
    # Sonra kısmi eşleştirme dene
    for col in df.columns:
        col_lower = col.lower()
        for name in possible_names:
            if name.lower() in col_lower or col_lower in name.lower():
                return col
    return None

# Test different searches
tests = [
    ['araç', 'araç no', 'tram', 'vehicle'],
    ['modül', 'sistem', 'module', 'system'],
    ['arıza sınıfı', 'failure class'],
]

for test in tests:
    result = get_column(df, test)
    print(f"\nSearching for {test}:")
    print(f"  Found: {result}")
