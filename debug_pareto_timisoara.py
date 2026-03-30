import sys
sys.path.insert(0, 'c:\\Users\\fatiherkin\\Desktop\\bozankaya_ssh_takip')

from routes.fracas import *
from flask import Flask
from utils.project_manager import ProjectManager

# Create a minimal Flask app context
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'

with app.app_context():
    # Load Timişoara data
    import pandas as pd
    excel_path = 'logs/timisoara/ariza_listesi/Fracas_TIMISOARA.xlsx'
    df = pd.read_excel(excel_path, sheet_name='FRACAS', header=3)
    df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
    
    # Filter non-empty FRACAS IDs
    fracas_col = None
    for col in df.columns:
        if 'fracas' in col.lower() and 'id' in col.lower():
            fracas_col = col
            break
    if fracas_col:
        df = df[df[fracas_col].notna()]
    
    print(f"Data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Test pareto analysis
    pareto = calculate_pareto_analysis(df)
    print(f"\nPareto by_module: {pareto['by_module']}")
    print(f"Pareto by_supplier length: {len(pareto['by_supplier'])}")
    print(f"Pareto by_location length: {len(pareto['by_location'])}")
    print(f"Pareto by_failure_class: {pareto['by_failure_class']}")
    
    # Test basic stats
    stats = calculate_basic_stats(df)
    print(f"\nBasic stats keys: {stats.keys()}")
    print(f"Stats: {stats}")
