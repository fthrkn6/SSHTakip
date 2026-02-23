"""
Equipment tablosunu km_data.json'dan gelen veriler ile güncelle
"""
import json
from app import create_app
from models import db, Equipment

app = create_app()

with app.app_context():
    print("[INFO] KM verilerini Equipment tablosuna yüklüyor...")

    # km_data.json'ı oku
    with open('./data/belgrad/km_data.json', 'r', encoding='utf-8') as f:
        km_data = json.load(f)

    # Equipment tablosunu güncelle
    update_count = 0
    for tram_id, data in km_data.items():
        if not tram_id:  # Boş ID'yi atla
            continue
        
        current_km = data.get('current_km', 0)
        
        # Veritabanında ara
        equipment = Equipment.query.filter_by(equipment_code=str(tram_id)).first()
        
        if equipment:
            old_km = equipment.current_km
            equipment.current_km = current_km
            print(f"  {tram_id}: {old_km:6d} -> {current_km:6d} km")
            update_count += 1
        else:
            print(f"  [WARN] {tram_id} veritabanında yok")

    # Değişiklikleri kaydet
    db.session.commit()
    print(f"\n[OK] {update_count} tramvay KM değeri güncellendi!")

    # Doğrulama
    print("\n[VERIFY] İlk 5 tramvay doğrulaması:")
    for tram_id in ['1531', '1532', '1533', '1534', '1535']:
        eq = Equipment.query.filter_by(equipment_code=tram_id).first()
        if eq:
            json_km = km_data.get(tram_id, {}).get('current_km', 0)
            match = "OK" if eq.current_km == json_km else "MISMATCH"
            print(f"  [{match}] {tram_id}: Equipment={eq.current_km:6d}, JSON={json_km:6d}")
