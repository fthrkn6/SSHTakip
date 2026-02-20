import os
import glob
from datetime import datetime

# Silinecek dosyaları topla
patterns = ['test_', 'debug_', 'check_', 'add_', 'analyze_', 'ANALYSIS', 'ARIZA_', 'ask_', 'apply_', 'architecture_', 'fix_', 'final_', 'create_', 'display_', 'export_', 'extract_', 'diagnose']

deleted_count = 0
backup_dir = '_backup_cleanup'

# Backup dir oluştur
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

for file in glob.glob('*.py'):
    if any(file.startswith(p) for p in patterns):
        try:
            backup_path = os.path.join(backup_dir, file)
            os.rename(file, backup_path)
            print(f"✓ Moved: {file} → {backup_dir}/")
            deleted_count += 1
        except Exception as e:
            print(f"✗ Error: {file} - {e}")

print(f"\n{'='*60}")
print(f"Taşınan dosya sayısı: {deleted_count}")
print(f"Backup konumu: {backup_dir}/")
print(f"NOT: Dosyalar silinmedi, taşındı. Gerekirse geri getir!")
print(f"Geri getirmek için: move {backup_dir}/*.py .")
