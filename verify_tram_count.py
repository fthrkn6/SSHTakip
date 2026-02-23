"""
Veriler.xlsx'ten kaç tram_id geldiğini kontrol et
"""
from app import create_app
from models import Equipment

app = create_app()

with app.app_context():
    # get_tram_ids_from_veriler fonksiyonunu kullan
    from routes.service_status import get_tram_ids_from_veriler
    
    current_project = 'belgrad'
    
    tram_ids = get_tram_ids_from_veriler(current_project)
    
    print(f"[INFO] Veriler.xlsx'ten belgrad projesi için tram_id sayısı: {len(tram_ids)}")
    print(f"[DATA] Tram ID'ler: {tram_ids[:30]}")  # İlk 30'u göster
    
    # Equipment tablosundaki tüm araclar
    all_equipment = Equipment.query.filter_by(project_code=current_project, parent_id=None).all()
    print(f"\n[EQUIPMENT] Equipment tablosundaki toplam araç: {len(all_equipment)}")
    
    # Veriler.xlsx'teki ile Equipment'teki fark
    equipment_codes = [eq.equipment_code for eq in all_equipment]
    in_veriler = sum(1 for tid in tram_ids if tid in equipment_codes)
    
    print(f"[OVERLAP] Veriler.xlsx'te ve Equipment'te olan: {in_veriler}")
    print(f"[OVERLAP] Sadece Equipment'te olan: {len(all_equipment) - in_veriler}")
