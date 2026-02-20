import os
import glob

# Silinebilecek dosya türleri
patterns = ['test_', 'debug_', 'check_', 'add_', 'analyze_', 'ANALYSIS', 'ARIZA_', 'ask_', 'apply_', 'architecture_', 'fix_', 'final_', 'create_', 'display_', 'export_', 'extract_', 'diagnose']

files_to_delete = []
total_size = 0

for file in glob.glob('*.py'):
    if any(file.startswith(p) for p in patterns):
        size = os.path.getsize(file)
        files_to_delete.append(file)
        total_size += size

print(f"Silinebilecek dosyalar ({len(files_to_delete)}):")
for f in sorted(files_to_delete):
    print(f"  - {f}")

print(f"\nToplam boyut: {total_size / 1024 / 1024:.2f} MB")
print(f"\n{'='*60}")
print("KORUNAN DOSYALAR (silinMEyecek):")
protected = ['app.py', 'models.py', 'config.py']
for f in sorted(glob.glob('*.py')):
    if f not in files_to_delete and f not in protected:
        print(f"  - {f}")
