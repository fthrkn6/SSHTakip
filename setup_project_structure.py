"""
Proje Klasör Yapısını Otomatik Oluşturma ve Yapılandırma
Mevcut logs klasörleri için yapı kurma
"""

import os
import json
import shutil
from datetime import datetime

def setup_project_structure():
    """logs klasöründeki tüm projeleri yapılandır"""
    root_path = os.getcwd()
    logs_path = os.path.join(root_path, 'logs')
    
    if not os.path.exists(logs_path):
        print(f"❌ logs klasörü bulunamadı: {logs_path}")
        return
    
    # logs klasöründeki klasörleri tarayıp proje klasörü olanları belirle
    projects = []
    
    for item in os.listdir(logs_path):
        item_path = os.path.join(logs_path, item)
        
        # Klasör mü ve geçerli proje mı kontrol et
        if os.path.isdir(item_path) and item not in ['archive', 'reports', 'service_status_history', 'history']:
            projects.append(item)
            
            # Her proje için klasör yapısını oluştur
            print(f"\n📁 Proje '{item}'  yapılandırılıyor...")
            
            # Gerekli klasörleri oluştur
            subdirs = ['veriler', 'ariza_listesi', 'config', 'archive']
            for subdir in subdirs:
                subdir_path = os.path.join(item_path, subdir)
                if not os.path.exists(subdir_path):
                    os.makedirs(subdir_path)
                    print(f"  ✓ Klasör oluşturuldu: {subdir}/")
                else:
                    print(f"  ✓ Klasör mevcuttu: {subdir}/")
            
            # Mevcut dosyaları uygun yerlere taşı
            migrate_project_files(item_path, item)
    
    print(f"\n✅ {len(projects)} proje yapılandırıldı: {', '.join(projects)}")
    return projects

def migrate_project_files(project_path, project_code):
    """
    Mevcut dosyaları uygun klasörlere taşı
    - Veriler.xlsx → veriler/
    - Fracas_*.xlsx → ariza_listesi/
    - Diğer Excel dosyaları → veriler/
    """
    print(f"  📄 Dosya taşınması başladı...")
    
    moved = 0
    
    # 1. ÖNCE: data/{project}/ klasöründeki dosyaları kontrol et
    root_path = os.path.dirname(os.path.dirname(project_path))
    data_project_path = os.path.join(root_path, 'data', project_code)
    
    if os.path.exists(data_project_path):
        print(f"    → data/{project_code}/ klasörü bulundu, dosyalar kopyalanıyor...")
        for file in os.listdir(data_project_path):
            file_path = os.path.join(data_project_path, file)
            
            if not os.path.isfile(file_path) or not file.endswith('.xlsx') or file.startswith('~$'):
                continue
            
            # Nereye taşıyacağını belirle
            if 'fracas' in file.lower():
                dest = 'ariza_listesi'
            elif 'veriler' in file.lower():
                dest = 'veriler'
            else:
                dest = 'veriler'
            
            dest_path = os.path.join(project_path, dest, file)
            
            # Zaten orada mı kontrol et
            if not os.path.exists(dest_path):
                try:
                    shutil.copy2(file_path, dest_path)
                    print(f"      → {file} → {dest}/")
                    moved += 1
                except Exception as e:
                    print(f"      ✗ {file} kopyalanamadı: {e}")
    
    # 2. SONRA: Proje klasöründeki dosyaları kontrol et
    for file in os.listdir(project_path):
        file_path = os.path.join(project_path, file)
        
        # Klasör değil dosya mı kontrol et
        if not os.path.isdir(file_path) and file.endswith('.xlsx') and not file.startswith('~$'):
            # Nereye taşıyacağını belirle
            if 'fracas' in file.lower():
                dest = 'ariza_listesi'
            elif 'veriler' in file.lower():
                dest = 'veriler'
            else:
                dest = 'veriler'
            
            dest_path = os.path.join(project_path, dest, file)
            
            # Zaten orada mı kontrol et
            if not os.path.exists(dest_path):
                try:
                    shutil.copy2(file_path, dest_path)
                    print(f"    → {file} → {dest}/")
                    moved += 1
                except Exception as e:
                    print(f"    ✗ {file} taşınamadı: {e}")
    
    print(f"  ✓ {moved} dosya kopyalandı")

def create_proje_config_for_project(project_code, project_path):
    """Her proje için proje_config.json oluştur"""
    config_dir = os.path.join(project_path, 'config')
    config_file = os.path.join(config_dir, 'proje_config.json')
    
    if os.path.exists(config_file):
        return
    
    config = {
        "project_code": project_code,
        "created": datetime.now().isoformat(),
        "settings": {
            "backup_enabled": True,
            "backup_frequency": "daily",
            "auto_backup_time": "05:00"
        }
    }
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"  ✓ proje_config.json oluşturuldu")
    except Exception as e:
        print(f"  ✗ config oluşturulamadı: {e}")

if __name__ == '__main__':
    print("🚀 Proje Yapı Kurulumu Başlatılıyor...\n")
    projects = setup_project_structure()
    
    # Her proje için config oluştur
    logs_path = os.path.join(os.getcwd(), 'logs')
    for project in projects:
        project_path = os.path.join(logs_path, project)
        create_proje_config_for_project(project, project_path)
    
    print("\n✅ Kurulum tamamlandı!")
