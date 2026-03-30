import pandas as pd
import os

projects = ['belgrad', 'gebze', 'istanbul', 'kayseri', 'kocaeli', 'iasi', 'samsun']

for project in projects:
    file_path = f'logs/{project}/ariza_listesi/Fracas_{project.upper()}.xlsx'
    
    if os.path.exists(file_path):
        print(f"\n{'='*60}")
        print(f"Project: {project.upper()}")
        print(f"{'='*60}")
        
        try:
            # Try header=0 (default)
            df_h0 = pd.read_excel(file_path, header=0)
            print(f"With header=0: Shape {df_h0.shape}")
            print(f"  First 3 columns: {list(df_h0.columns[:3])}")
            
            # Try header=3
            df_h3 = pd.read_excel(file_path, header=3)
            print(f"With header=3: Shape {df_h3.shape}")
            print(f"  First 3 columns: {list(df_h3.columns[:3])}")
            
            # Check if data looks valid
            print(f"  First 3 actual data rows (header=3):")
            print(df_h3.head(3).to_string())
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"\n{project.upper()}: File not found at {file_path}")
