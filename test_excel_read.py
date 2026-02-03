import pandas as pd
import os

# Direct path to FRACAS file
fracas_file = r"C:\Users\ferki\Desktop\bozankaya_ssh_takip\data\belgrad\BEL25_FRACAS(Hata Raporlama Analizi ve Düzeltici Aksiyon Sitemi) Formu - 2025.12.3 S.xlsx"

print(f"File exists: {os.path.exists(fracas_file)}")

if os.path.exists(fracas_file):
    df = pd.read_excel(fracas_file, sheet_name='FRACAS', header=3)
    df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
    
    # Find FRACAS ID column
    fracas_col = None
    for col in df.columns:
        if 'fracas' in col.lower() and 'id' in col.lower():
            fracas_col = col
            break
    
    print(f"FRACAS column: {fracas_col}")
    print(f"DataFrame shape: {df.shape}")
    
    if fracas_col:
        df_clean = df[df[fracas_col].notna()].copy()
        print(f"Non-empty rows: {len(df_clean)}")
        
        if len(df_clean) > 0:
            print(f"\nFirst 3 FRACAS IDs:")
            for fracas_id in df_clean[fracas_col].head(3):
                print(f"  - {fracas_id}")
