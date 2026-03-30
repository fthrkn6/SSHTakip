import pandas as pd
import os
from app import create_app
from utils.project_manager import ProjectManager

app = create_app()
with app.app_context():
    # Load Timişoara data
    excel_path = ProjectManager.get_fracas_file('timisoara')
print(f"Excel path: {excel_path}")
print(f"File exists: {os.path.exists(excel_path)}")

if excel_path and os.path.exists(excel_path):
    # Try header=3 (for logs/ format)
    if 'logs' in excel_path and 'ariza_listesi' in excel_path:
        df = pd.read_excel(excel_path, sheet_name='FRACAS', header=3)
    else:
        df = pd.read_excel(excel_path, sheet_name='FRACAS', header=0)
    
        # Normalize columns - match the routes/fracas.py logic
        df.columns = df.columns.str.replace('\n', ' ', regex=False).str.replace('\r', '', regex=False)
        df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
