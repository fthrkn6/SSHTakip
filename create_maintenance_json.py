import json
import os

projects = ['iasi', 'kayseri', 'kocaeli', 'gebze', 'timisoara']

# Basit maintenance template
template = {
    "15K": {
        "km": 15000,
        "works": ["BOZ-001"]
    },
    "30K": {
        "km": 30000,
        "works": ["BOZ-002"]
    },
    "60K": {
        "km": 60000,
        "works": ["BOZ-003", "BOZ-004"]
    },
    "90K": {
        "km": 90000,
        "works": ["BOZ-005"]
    },
    "120K": {
        "km": 120000,
        "works": ["BOZ-006", "BOZ-007"]
    },
    "200K": {
        "km": 200000,
        "works": ["BOZ-008"]
    }
}

print("=== Bakım JSON Dosyaları Oluşturuluyor ===\n")

for proj in projects:
    file_path = f'data/{proj}/maintenance.json'
    
    # Dosya zaten varsa pas geç (overwrite etme!)
    if os.path.exists(file_path):
        print(f"✓ {proj}: maintenance.json zaten var, pas geç")
        continue
    
    # Klasör var mı kontrol et, yoksa oluştur
    os.makedirs(f'data/{proj}', exist_ok=True)
    
    # Dosya oluştur
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"✓ {proj}: maintenance.json oluşturuldu")

print("\n✓ Tüm projeler için maintenance.json hazır!")
