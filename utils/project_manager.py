"""
Proje Yönetim Sistemi
Her proje logs/{project_code}/ klasöründen veri okur ve yazar
"""

import os
import json
import shutil
from datetime import datetime
from flask import current_app, session
import pandas as pd

class ProjectManager:
    """Proje yönetimi ve veri erişimi"""
    
    CONFIG_FILE = 'projects_config.json'
    
    @staticmethod
    def get_config_path():
        """projects_config.json dosya yolunu döndür"""
        return os.path.join(current_app.root_path, ProjectManager.CONFIG_FILE)
    
    @staticmethod
    def load_projects():
        """projects_config.json'dan tüm projeleri yükle"""
        config_path = ProjectManager.get_config_path()
        
        if not os.path.exists(config_path):
            return [], {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get('projects', []), config.get('defaults', {})
        except Exception as e:
            print(f"Proje konfigürasyonu yüklenirken hata: {e}")
            return [], {}
    
    @staticmethod
    def get_all_projects():
        """Tüm projeleri (aktif + pasif) listele"""
        projects, _ = ProjectManager.load_projects()
        return projects
    
    @staticmethod
    def get_active_projects():
        """Sadece aktif projeleri listele"""
        projects, _ = ProjectManager.load_projects()
        return [p for p in projects if p.get('status') == 'aktif']
    
    @staticmethod
    def get_project(project_code):
        """Belirli bir projeyi getir"""
        projects, _ = ProjectManager.load_projects()
        for project in projects:
            if project.get('code') == project_code:
                return project
        return None
    
    @staticmethod
    def get_default_project():
        """Varsayılan projeyi getir"""
        _, defaults = ProjectManager.load_projects()
        return defaults.get('default_project', 'belgrad')
    
    @staticmethod
    def get_current_project():
        """Session'dan aktif projeyi al (yoksa varsayılan)"""
        return session.get('current_project', ProjectManager.get_default_project())
    
    @staticmethod
    def set_current_project(project_code):
        """Session'da aktif projeyi ayarla"""
        if ProjectManager.get_project(project_code):
            session['current_project'] = project_code
            return True
        return False
    
    @staticmethod
    def get_project_path(project_code):
        """Projenin ana klasör yolunu döndür: logs/{project_code}/"""
        return os.path.join(current_app.root_path, 'logs', project_code)
    
    @staticmethod
    def get_veriler_file(project_code):
        """Projenin Veriler.xlsx dosya yolunu döndür - data/{project}/Veriler.xlsx'den çek"""
        root_path = current_app.root_path
        
        # Öncelik: data/{project}/Veriler.xlsx (KULLANICI TERCIH)
        veriler_path = os.path.join(root_path, 'data', project_code, 'Veriler.xlsx')
        if os.path.exists(veriler_path):
            return veriler_path
        
        # Fallback: logs/{project}/veriler/Veriler.xlsx (eski konum)
        project_path = ProjectManager.get_project_path(project_code)
        old_veriler = os.path.join(project_path, 'veriler', 'Veriler.xlsx')
        if os.path.exists(old_veriler):
            return old_veriler
        
        # Fallback: logs/{project}/data/Veriler.xlsx
        data_path = os.path.join(project_path, 'data', 'Veriler.xlsx')
        if os.path.exists(data_path):
            return data_path
        
        # Fallback: logs/{project}/Veriler.xlsx
        root_veriler = os.path.join(project_path, 'Veriler.xlsx')
        if os.path.exists(root_veriler):
            return root_veriler
        
        return None
    
    @staticmethod
    def get_fracas_file(project_code):
        """Projenin Fracas_{project_code}.xlsx dosya yolunu döndür"""
        project_path = ProjectManager.get_project_path(project_code)
        ariza_dir = os.path.join(project_path, 'ariza_listesi')
        
        if os.path.exists(ariza_dir):
            # Project-specific FRACAS dosyasını ara (örn: Fracas_BELGRAD.xlsx)
            project_file_map = {
                'belgrad': 'Fracas_BELGRAD.xlsx',
                'gebze': 'Fracas_GEBZE.xlsx',
                'iasi': 'Fracas_IASI.xlsx',
                'kayseri': 'Fracas_KAYSERİ.xlsx',
                'kocaeli': 'Fracas_KOCAELI.xlsx',
                'timisoara': 'Fracas_TIMISOARA.xlsx'
            }
            
            specific_fracas = project_file_map.get(project_code)
            if specific_fracas:
                specific_file = os.path.join(ariza_dir, specific_fracas)
                if os.path.exists(specific_file):
                    return specific_file
            
            # Fallback: varsa başka Fracas_*.xlsx
            for file in os.listdir(ariza_dir):
                if file.upper().startswith('FRACAS_') and file.endswith('.xlsx') and not file.startswith('~$'):
                    return os.path.join(ariza_dir, file)
        
        return None
    
    @staticmethod
    def get_project_structure(project_code):
        """Projenin klasör yapısını kontrol et ve döndür"""
        project_path = ProjectManager.get_project_path(project_code)
        
        structure = {
            'project_code': project_code,
            'project_path': project_path,
            'exists': os.path.exists(project_path),
            'veriler_file': ProjectManager.get_veriler_file(project_code),
            'fracas_file': ProjectManager.get_fracas_file(project_code),
            'subdirs': {
                'veriler': os.path.join(project_path, 'veriler'),
                'data': os.path.join(project_path, 'data'),
                'ariza_listesi': os.path.join(project_path, 'ariza_listesi'),
                'config': os.path.join(project_path, 'config'),
                'archive': os.path.join(project_path, 'archive')
            }
        }
        
        return structure
    
    @staticmethod
    def add_project(project_code, name, description="", location=""):
        """
        Yeni proje ekle
        - projects_config.json'a kaydını ekle
        - logs/{project}/ klasör yapısını oluştur
        """
        # Zaten var mı kontrol et
        if ProjectManager.get_project(project_code):
            return False, "Proje zaten var"
        
        # projects_config.json güncelleştir
        config_path = ProjectManager.get_config_path()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            new_project = {
                "code": project_code,
                "name": name,
                "description": description,
                "location": location,
                "status": "aktif",
                "created": datetime.now().strftime("%Y-%m-%d"),
                "admin": "admin@bozankaya.com"
            }
            
            config['projects'].append(new_project)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # Klasör yapısını oluştur
            project_path = ProjectManager.get_project_path(project_code)
            os.makedirs(os.path.join(project_path, 'veriler'), exist_ok=True)
            os.makedirs(os.path.join(project_path, 'ariza_listesi'), exist_ok=True)
            os.makedirs(os.path.join(project_path, 'config'), exist_ok=True)
            os.makedirs(os.path.join(project_path, 'archive'), exist_ok=True)
            
            return True, f"Proje '{name}' başarıyla oluşturuldu"
        
        except Exception as e:
            return False, f"Hata: {str(e)}"
    
    @staticmethod
    def delete_project(project_code, hard_delete=False):
        """
        Projeyi sil (soft delete = arşivle)
        - Soft delete: status='arşivlendi', klasör korunur
        - Hard delete: klasör silinir (ama yedek /archive altında tutulur)
        """
        project = ProjectManager.get_project(project_code)
        if not project:
            return False, "Proje bulunamadı"
        
        config_path = ProjectManager.get_config_path()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if hard_delete:
                # Klasörü arşive taşı
                project_path = ProjectManager.get_project_path(project_code)
                archive_parent = os.path.join(current_app.root_path, 'logs', 'archive')
                os.makedirs(archive_parent, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                archive_path = os.path.join(archive_parent, f"{project_code}_{timestamp}")
                
                if os.path.exists(project_path):
                    shutil.copytree(project_path, archive_path)
                    shutil.rmtree(project_path)
                
                # Config'ten tamamen kaldır
                config['projects'] = [p for p in config['projects'] if p['code'] != project_code]
            else:
                # Soft delete: status'ü 'arşivlendi' yap
                for p in config['projects']:
                    if p['code'] == project_code:
                        p['status'] = 'arşivlendi'
                        p['archived_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        break
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True, f"Proje '{project_code}' arşivlendi"
        
        except Exception as e:
            return False, f"Hata: {str(e)}"
    
    @staticmethod
    def load_veriler_excel(project_code):
        """Projenin Veriler.xlsx dosyasını Pandas DataFrame olarak yükle"""
        veriler_file = ProjectManager.get_veriler_file(project_code)
        
        if not veriler_file or not os.path.exists(veriler_file):
            return None
        
        try:
            df = pd.read_excel(veriler_file)
            return df
        except Exception as e:
            print(f"Veriler.xlsx yüklenirken hata ({project_code}): {e}")
            return None


# Kolay erişim helper'ları
def get_current_project():
    """Session'dan aktif projeyi getir"""
    return ProjectManager.get_current_project()

def get_veriler_file(project_code=None):
    """Veriler.xlsx yolunu getir (proje kodu verilmezse aktif proje kullanılır)"""
    if not project_code:
        project_code = ProjectManager.get_current_project()
    return ProjectManager.get_veriler_file(project_code)

def get_fracas_file(project_code=None):
    """Fracas_*.xlsx yolunu getir"""
    if not project_code:
        project_code = ProjectManager.get_current_project()
    return ProjectManager.get_fracas_file(project_code)

def load_veriler_excel(project_code=None):
    """Veriler.xlsx'i DataFrame olarak yükle"""
    if not project_code:
        project_code = ProjectManager.get_current_project()
    return ProjectManager.load_veriler_excel(project_code)
