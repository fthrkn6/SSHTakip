"""
Yedekleme Yönetim Sistemi
Her form gönderişinde + otomatik günlük yedek
Veriler kayıp koruması maksimum
"""

import os
import shutil
import zipfile
import json
from datetime import datetime
from flask import current_app
from utils.project_manager import ProjectManager

class BackupManager:
    """Dosya yedekleme ve geri yükleme"""
    
    @staticmethod
    def get_archive_path(project_code):
        """Projenin arşiv klasörü"""
        project_path = ProjectManager.get_project_path(project_code)
        archive_path = os.path.join(project_path, 'archive')
        os.makedirs(archive_path, exist_ok=True)
        return archive_path
    
    @staticmethod
    def backup_file(file_path, project_code=None):
        """
        Tek bir dosya yedekle
        logs/{project}/archive/{filename}_YYYYMMDD_HHMMSS.xlsx
        """
        if not os.path.exists(file_path):
            return False, "Dosya bulunamadı"
        
        try:
            if not project_code:
                # Dosya yolundan proje kodunu çıkar
                path_parts = file_path.split(os.sep)
                project_code = path_parts[-3] if len(path_parts) >= 3 else 'belgrad'
            
            archive_path = BackupManager.get_archive_path(project_code)
            
            # Timestamp ile yedek dosya adı
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            name_without_ext = os.path.splitext(filename)[0]
            backup_filename = f"{name_without_ext}_backup_{timestamp}.xlsx"
            backup_path = os.path.join(archive_path, backup_filename)
            
            # Dosyayı kopyala
            shutil.copy2(file_path, backup_path)
            
            # Yedek logu tut
            BackupManager._log_backup(project_code, filename, backup_filename)
            
            return True, f"Yedek alındı: {backup_filename}"
        
        except Exception as e:
            return False, f"Yedekleme hatası: {str(e)}"
    
    @staticmethod
    def backup_project_full(project_code):
        """
        Tüm projeyi tam olarak yedekle
        logs/archive/{project_code}_YYYYMMDD_HHMMSS/
        """
        project_path = ProjectManager.get_project_path(project_code)
        
        if not os.path.exists(project_path):
            return False, "Proje klasörü bulunamadı"
        
        try:
            # Arşiv klasörü
            archive_parent = os.path.join(current_app.root_path, 'logs', 'archive')
            os.makedirs(archive_parent, exist_ok=True)
            
            # Zaman damgalı klasör
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            archive_dir = os.path.join(archive_parent, f"{project_code}_{timestamp}")
            
            # Tam kopyası
            shutil.copytree(project_path, archive_dir)
            
            # Arşiv logu
            BackupManager._log_full_backup(project_code, archive_dir)
            
            return True, f"Tam yedek alındı: {archive_dir}"
        
        except Exception as e:
            return False, f"Tam yedekleme hatası: {str(e)}"
    
    @staticmethod
    def backup_all_projects():
        """Tüm projeleri yedekle"""
        projects = ProjectManager.get_active_projects()
        results = []
        
        for project in projects:
            project_code = project.get('code')
            success, message = BackupManager.backup_project_full(project_code)
            results.append({
                'project': project_code,
                'success': success,
                'message': message
            })
        
        return results
    
    @staticmethod
    def restore_file(file_path, backup_filename):
        """
        Backup dosyasından dosyayı geri yükle
        """
        if not os.path.exists(backup_filename):
            return False, "Yedek dosyası bulunamadı"
        
        try:
            # Orijinal dosyayı yedekle (restore öncesi)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_backup = file_path + f".before_restore_{timestamp}"
            shutil.copy2(file_path, original_backup)
            
            # Yedekten geri yükle
            shutil.copy2(backup_filename, file_path)
            
            return True, f"Dosya geri yüklendi. Eski sürüm: {original_backup}"
        
        except Exception as e:
            return False, f"Geri yükleme hatası: {str(e)}"
    
    @staticmethod
    def restore_project(project_code, backup_timestamp):
        """
        Projeyi belirli bir tarihten geri yükle
        """
        archive_parent = os.path.join(current_app.root_path, 'logs', 'archive')
        backup_dir = os.path.join(archive_parent, f"{project_code}_{backup_timestamp}")
        
        if not os.path.exists(backup_dir):
            return False, "Yedek bulunamadı"
        
        try:
            project_path = ProjectManager.get_project_path(project_code)
            
            # Restore öncesi güncel sürümü arşivle
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            current_backup = os.path.join(archive_parent, f"{project_code}_current_{timestamp}")
            shutil.copytree(project_path, current_backup)
            
            # Eski sürümü geri yükle
            shutil.rmtree(project_path)
            shutil.copytree(backup_dir, project_path)
            
            return True, f"Proje geri yüklendi. Güncel sürüm: {current_backup}"
        
        except Exception as e:
            return False, f"Restore hatası: {str(e)}"
    
    @staticmethod
    def get_backup_history(project_code):
        """Projenin yedek geçmişini listele"""
        archive_path = BackupManager.get_archive_path(project_code)
        
        backups = []
        if os.path.exists(archive_path):
            for file in sorted(os.listdir(archive_path), reverse=True):
                file_path = os.path.join(archive_path, file)
                if os.path.isfile(file_path) and file.endswith('.xlsx'):
                    stat = os.stat(file_path)
                    backups.append({
                        'filename': file,
                        'path': file_path,
                        'size': stat.st_size,
                        'date': datetime.fromtimestamp(stat.st_mtime)
                    })
        
        return backups
    
    @staticmethod
    def _log_backup(project_code, original_file, backup_file):
        """Yedek işlemini loga yaz"""
        project_path = ProjectManager.get_project_path(project_code)
        log_file = os.path.join(project_path, 'archive', '.backup_log.json')
        
        try:
            log_data = []
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            
            log_data.append({
                'timestamp': datetime.now().isoformat(),
                'original': original_file,
                'backup': backup_file,
                'type': 'single_file'
            })
            
            # Son 100 kaydı tut
            log_data = log_data[-100:]
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"Yedek logu yazılamadı: {e}")
    
    @staticmethod
    def _log_full_backup(project_code, archive_dir):
        """Tam yedek işlemini loga yaz"""
        project_path = ProjectManager.get_project_path(project_code)
        log_file = os.path.join(project_path, 'archive', '.backup_log.json')
        
        try:
            log_data = []
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            
            log_data.append({
                'timestamp': datetime.now().isoformat(),
                'path': archive_dir,
                'type': 'full_backup'
            })
            
            log_data = log_data[-100:]
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"Tam yedek logu yazılamadı: {e}")
    
    @staticmethod
    def cleanup_old_backups(project_code, days=30):
        """
        Belirli gün sayısından eski yedekleri sil
        Örnek: 30 günden eski yedekler silinir
        """
        from datetime import timedelta
        
        archive_path = BackupManager.get_archive_path(project_code)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted = 0
        try:
            for file in os.listdir(archive_path):
                file_path = os.path.join(archive_path, file)
                if os.path.isfile(file_path):
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_mtime < cutoff_date:
                        os.remove(file_path)
                        deleted += 1
        except Exception as e:
            print(f"Eski yedekler silinirken hata: {e}")
        
        return deleted
