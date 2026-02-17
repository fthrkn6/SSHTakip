"""
Proje Yönetim Sistemi Test Scripti
"""

import os
from flask import Flask, session
from utils.project_manager import ProjectManager
from utils.backup_manager import BackupManager

# Test Flask uygulaması
app = Flask(__name__)
app.secret_key = 'test'

with app.app_context():
    print("🧪 Proje Yönetim Sistemi Test\n")
    
    # Test 1: Projeleri yükle
    print("1️⃣  Projeleri Yükle:")
    projects = ProjectManager.get_all_projects()
    for p in projects:
        print(f"   - {p['code']:15} | {p['name']:25} | {p.get('status', 'bilinmiyor')}")
    
    print(f"\n   ✅ {len(projects)} proje yüklendi")
    
    # Test 2: Belgrad projesi yapısını kontrol et
    print("\n2️⃣  Belgrad Proje Yapısı:")
    structure = ProjectManager.get_project_structure('belgrad')
    print(f"   - Path: {structure['project_path']}")
    print(f"   - Exists: {structure['exists']}")
    print(f"   - Veriler.xlsx: {structure['veriler_file']}")
    print(f"   - Fracas.xlsx: {structure['fracas_file']}")
    
    # Test 3: Veriler dosyasını yükle
    print("\n3️⃣  Veriler.xlsx Yükleme (Belgrad):")
    df = ProjectManager.load_veriler_excel('belgrad')
    if df is not None:
        print(f"   ✅ Yüklendi! Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)[:5]}")
    else:
        print(f"   ⚠️  Veriler.xlsx bulunamadı")
    
    # Test 4: Tüm projelerin Veriler.xlsx'ini kontrol et
    print("\n4️⃣  Tüm Projelerin Veriler.xlsx Durumu:")
    for p in projects:
        code = p['code']
        veriler_file = ProjectManager.get_veriler_file(code)
        if veriler_file and os.path.exists(veriler_file):
            print(f"   ✓ {code:15} → {veriler_file}")
        else:
            print(f"   ✗ {code:15} → Veriler.xlsx bulunamadı")
    
    # Test 5: Yedek işlemi
    print("\n5️⃣  Yedek İşlemi (Belgrad):")
    belgrad_fracas = ProjectManager.get_fracas_file('belgrad')
    if belgrad_fracas and os.path.exists(belgrad_fracas):
        success, msg = BackupManager.backup_file(belgrad_fracas, 'belgrad')
        print(f"   {'✅' if success else '❌'} {msg}")
    else:
        print(f"   ⚠️  Fracas.xlsx bulunamadı")
    
    # Test 6: Yedek geçmişini kontrol et
    print("\n6️⃣  Yedek Geçmişi (Belgrad):")
    backups = BackupManager.get_backup_history('belgrad')
    for backup in backups[:3]:  # Son 3 yedek
        print(f"   - {backup['filename']}")
    if len(backups) == 0:
        print(f"   (Henüz yedek yok)")
    
    print("\n✅ Testler tamamlandı!")
