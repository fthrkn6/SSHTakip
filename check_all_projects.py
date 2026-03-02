import pandas as pd
import os

projects = ['belgrad', 'gebze', 'iasi', 'kayseri', 'kocaeli', 'timisoara']

print("All projects' equipment codes:\n")
for proj in projects:
    excel_path = f'data/{proj}/Veriler.xlsx'
    try:
        if os.path.exists(excel_path):
            df = pd.read_excel(excel_path, sheet_name='Sayfa2', header=0, engine='openpyxl')
            first_col = df.columns[0]
            codes = sorted(df[first_col].dropna().unique())
            codes = [int(c) if isinstance(c, (int, float)) else c for c in codes]
            print(f"{proj:12}: {codes[:5]}...{codes[-5:] if len(codes) > 5 else codes}")
            
            # Check for 4001-4022
            if any(4001 <= int(c) <= 4022 for c in codes if isinstance(c, int)):
                print(f"             ✓ Contains 4001-4022 range")
    except Exception as e:
        print(f"{proj:12}: ERROR - {e}")
