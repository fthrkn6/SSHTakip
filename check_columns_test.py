import pandas as pd
import os
from app import create_app
from utils.project_manager import ProjectManager
from routes.fracas import get_column

app = create_app()
with app.app_context():
    # Load Timişoara data
    excel_path = ProjectManager.get_fracas_file('timisoara')
    
    if excel_path and os.path.exists(excel_path):
        # Try header=3 (for logs/ format)
        if 'logs' in excel_path and 'ariza_listesi' in excel_path:
            df = pd.read_excel(excel_path, sheet_name='FRACAS', header=3)
        else:
            df = pd.read_excel(excel_path, sheet_name='FRACAS', header=0)
        
        # Normalize columns - match the routes/fracas.py logic
        df.columns = df.columns.str.replace('\n', ' ', regex=False).str.replace('\r', '', regex=False)
        df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
        
        print(f"Total columns: {len(df.columns)}")
        print(f"DataFrame shape: {df.shape}\n")
        
        # Test which columns are found
        test_cases = [
            (['araç module', 'vehicle module', 'modül'], 'Vehicle Module'),
            (['tedarikçi', 'supplier', 'relevant supplier'], 'Supplier'),
            (['sistem', 'alt sistem', 'failure location', 'location'], 'Location/System'),
            (['arıza sınıfı', 'failure class', 'sınıf', 'failure'], 'Failure Class'),
        ]
        
        print("=" * 80)
        print("COLUMN MATCHING TEST")
        print("=" * 80)
        for search_names, label in test_cases:
            found_col = get_column(df, search_names)
            print(f"\n{label} (searching for: {search_names})")
            print(f"  Found: {found_col}")
            if found_col:
                print(f"  Sample values: {df[found_col].head(3).tolist()}")
        
        print("\n" + "=" * 80)        
        print("FIRST 15 COLUMNS (normalized):")
        print("=" * 80)
        for i, col in enumerate(df.columns[:15], 1):
            print(f"  {i}. '{col}'")
