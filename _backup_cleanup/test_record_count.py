import os
import pandas as pd

ariza_dir = r'c:\Users\ferki\Desktop\bozankaya_ssh_takip\logs\belgrad\ariza_listesi'

print("=== Checking Fracas_BELGRAD.xlsx ===")
for filename in os.listdir(ariza_dir):
    if filename.upper().startswith('FRACAS_') and filename.endswith('.xlsx'):
        excel_path = os.path.join(ariza_dir, filename)
        df = pd.read_excel(excel_path, sheet_name='FRACAS', header=3)
        print(f'File: {filename}')
        print(f'Records before filter: {len(df)}')
        
        df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
        for col in df.columns:
            if 'fracas' in col.lower() and 'id' in col.lower():
                df_filtered = df[df[col].notna()]
                print(f'Records after filter: {len(df_filtered)}')
                break
