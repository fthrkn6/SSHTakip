from utils.project_manager import ProjectManager
from app import create_app
import os
import pandas as pd

app = create_app()

with app.app_context():
    for project in ['belgrad', 'timisoara']:
        fracas_file = ProjectManager.get_fracas_file(project)
        exists = os.path.exists(fracas_file) if fracas_file else False
        print(f"\n{project.upper()}:")
        print(f"  Dosya: {fracas_file}")
        print(f"  Var Mı: {exists}")
        
        if exists:
            try:
                if 'logs' in fracas_file and 'ariza_listesi' in fracas_file:
                    df = pd.read_excel(fracas_file, sheet_name='FRACAS', header=3)
                else:
                    df = pd.read_excel(fracas_file, sheet_name='FRACAS', header=0)
                print(f"  Yüklenen: {len(df)} satır ✓")
            except Exception as e:
                print(f"  Hata: {e} ✗")
