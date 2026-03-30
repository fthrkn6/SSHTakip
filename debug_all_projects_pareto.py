"""
Debug script to check FRACAS data loading for all projects
"""
import sys
sys.path.insert(0, 'c:\\Users\\fatiherkin\\Desktop\\bozankaya_ssh_takip')

from routes.fracas import *
import pandas as pd
from flask import Flask
from utils.project_manager import ProjectManager

# Create a minimal Flask app context  
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'

projects = ['belgrad', 'gebze', 'istanbul', 'kayseri', 'kocaeli', 'timisoara', 'iasi', 'samsun']

with app.app_context():
    for project in projects:
        print(f"\n{'='*60}")
        print(f"Project: {project.upper()}")
        print(f"{'='*60}")
        
        excel_path = ProjectManager.get_fracas_file(project)
        print(f"Path: {excel_path}")
        
        if excel_path:
            try:
                # Simulate load_fracas_data
                df = pd.read_excel(excel_path, sheet_name='FRACAS', header=3)
                df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
                fracas_col = None
                for col in df.columns:
                    if 'fracas' in col.lower() and 'id' in col.lower():
                        fracas_col = col
                        break
                if fracas_col:
                    df = df[df[fracas_col].notna()]
                
                # Simulate pareto analysis
                pareto = calculate_pareto_analysis(df)
                
                print(f"Data shape: {df.shape}")
                print(f"Charts:")
                print(f"  by_module: {len(pareto['by_module'])} items")
                print(f"  by_supplier: {len(pareto['by_supplier'])} items")
                print(f"  by_location: {len(pareto['by_location'])} items")
                print(f"  by_failure_class: {len(pareto['by_failure_class'])} items")
                
                # Check if any are empty
                if not pareto['by_module']:
                    print("  WARNING: No module data!")
                if not pareto['by_supplier']:
                    print("  WARNING: No supplier data!")
                if not pareto['by_location']:
                    print("  WARNING: No location data!")
                if not pareto['by_failure_class']:
                    print("  WARNING: No failure class data!")
                    
            except Exception as e:
                print(f"ERROR: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("Path not found!")
