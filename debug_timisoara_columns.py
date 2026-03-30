import pandas as pd
import os
import sys

# Check Timişoara file
timisoara_file = 'logs/timisoara/ariza_listesi/Fracas_TIMISOARA.xlsx'
print(f'File exists: {os.path.exists(timisoara_file)}')

if os.path.exists(timisoara_file):
    try:
        df = pd.read_excel(timisoara_file)
        print(f'\nShape: {df.shape}')
        print(f'\nColumns ({len(df.columns)}):')
        for i, col in enumerate(df.columns):
            print(f'  {i}: "{col}"')
        print(f'\nFirst row sample:')
        print(df.iloc[0] if len(df) > 0 else 'No data')
    except Exception as e:
        print(f'Error reading file: {e}')
        import traceback
        traceback.print_exc()
else:
    print(f'File not found at {timisoara_file}')
    # List what exists
    base = 'logs/timisoara'
    if os.path.exists(base):
        print(f'\nContents of {base}:')
        for root, dirs, files in os.walk(base):
            level = root.replace(base, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f'{subindent}{file}')
