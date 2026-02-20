#!/usr/bin/env python3
"""Show exact Excel file path"""
import sys
sys.path.insert(0, '.')

from app import create_app
from utils.project_manager import ProjectManager
import os

app = create_app()

with app.app_context():
    project = 'belgrad'
    
    print("\n" + "="*100)
    print("EXCEL DOSYA YOLU")
    print("="*100 + "\n")
    
    print(f"1. APP KOKU (root_path):")
    print(f"   {app.root_path}\n")
    
    print(f"2. PROJE KLASSORU (get_project_path):")
    project_path = ProjectManager.get_project_path(project)
    print(f"   {project_path}\n")
    
    print(f"3. VERILER.XLSX DOSYA YOLU (get_veriler_file):")
    veriler_file = ProjectManager.get_veriler_file(project)
    print(f"   {veriler_file}\n")
    
    print(f"4. DOSYA VAR MI?")
    existe = os.path.exists(veriler_file)
    print(f"   {existe}\n")
    
    if existe:
        size = os.path.getsize(veriler_file)
        print(f"5. DOSYA BILGISI:")
        print(f"   Boyut: {size} bytes\n")
    
    # Klasor icerigi goster
    print(f"6. KLASOR ICERIGI (logs/belgrad/):")
    belgrad_path = os.path.join(app.root_path, 'logs', 'belgrad')
    if os.path.exists(belgrad_path):
        items = os.listdir(belgrad_path)
        for item in sorted(items):
            item_path = os.path.join(belgrad_path, item)
            if os.path.isdir(item_path):
                print(f"   [DIR]  {item}/")
            else:
                print(f"   [FILE] {item}")
    
    print("\n" + "="*100)
    print("OZET")
    print("="*100)
    print(f"\nDosya Konumu:   {veriler_file}")
    print(f"Dosya Adi:      Veriler.xlsx")
    print(f"Klasor:         logs/belgrad/veriler/")
    print(f"Sutu (tram_id): tram_id adli sutundan araç IDs okunuyor")
    print("\n" + "="*100 + "\n")
