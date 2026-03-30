from utils.project_manager import ProjectManager
from app import create_app
import os

app = create_app()

print("ProjectManager Test:")
print()

with app.app_context():
    for project in ['belgrad', 'timisoara', 'istanbul']:
        fracas_file = ProjectManager.get_fracas_file(project)
        exists = 'EXISTS' if fracas_file and os.path.exists(fracas_file) else 'MISSING'
        print(f"{project:15} -> {fracas_file}")
        print(f"                    [{exists}]")
        print()
