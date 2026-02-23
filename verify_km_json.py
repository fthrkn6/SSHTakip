"""
Equipment tablosunu km_data.json verilerine göre güncelle
"""
import json
import sys

# Import modelleri
try:
    # config.py'döndeki dotenv hatası için kütüphane yükle
    import os
    os.environ.setdefault('FLASK_SQLALCHEMY_DATABASE_URI', 'postgresql://user:password@localhost/bozankaya')
    
    import importlib.util
    spec = importlib.util.spec_from_file_location("models", "models.py")
    models = importlib.util.module_from_spec(spec)
    
    # models.py import yapıldığında config.py çağrılacak, dotenv eksikse hafife al
    spec.loader.exec_module(models)
    
    Equipment = models.Equipment
    db = models.db
    
    print("[SETUP] Models yüklendi")
except Exception as e:
    print(f"[WARNING] Model yükleme sorunlu: {e}")
    print("[INFO] Alternatif yol: Direkt SQL ile update yapacağız")

# km_data.json'ı oku
with open('./data/belgrad/km_data.json', 'r', encoding='utf-8') as f:
    km_data = json.load(f)

print(f"[INFO] km_data.json'da {len(km_data)} tramvay bulundu")
print("[DATA] Tramvay KM değerleri:")

for tram_id, data in km_data.items():
    if tram_id:  # Boş ID'yi atla
        current_km = data.get('current_km', 0)
        print(f"  {tram_id}: {current_km:6d} km")

print("\n[NOTE] Equipment tablosunu güncellemek için app.py'de KMDataManager.sync_json_to_equipment() çağırılması gerek")
