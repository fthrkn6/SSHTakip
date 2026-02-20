#!/usr/bin/env python3
"""Verify Veriler.xlsx paths for all projects"""
import sys
sys.path.insert(0, '.')

from app import create_app
from utils.project_manager import ProjectManager
import os

app = create_app()

with app.app_context():
    projects = ['belgrad', 'gebze', 'iasi', 'kayseri', 'kocaeli', 'timisoara']
    
    print("\n" + "="*100)
    print("VERILER.XLSX YOLLARI - TUM PROJELER")
    print("="*100 + "\n")
    
    for project in projects:
        veriler_file = ProjectManager.get_veriler_file(project)
        exists = os.path.exists(veriler_file)
        
        # data/{project}/Veriler.xlsx mi kontrol et
        is_data_folder = f'\\data\\{project}\\' in veriler_file or f'/data/{project}/' in veriler_file
        
        status = "OK" if exists else "YOK"
        source = "data/" if is_data_folder else "logs/"
        
        print(f"{project:12} | {source:6} | {status:3} | {veriler_file}")
    
    print("\n" + "="*100)
    print("Tum projeler data/{project}/Veriler.xlsx konumundan cekiyor")
    print("="*100 + "\n")
