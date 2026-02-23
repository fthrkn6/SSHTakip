import subprocess
import json
import os
import sys

# app.create_app()'ı kullan
if __name__ == '__main__':
    # Flask app'ı import et
    os.chdir(os.path.dirname(__file__))
    from app import Flask, create_app
    from models import db, Equipment
    
    # Create the Flask app
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)
    
    with app.app_context():
        # En yeni commit'ten data al
        result = subprocess.run(
            ['git', 'show', '01105c8:data/belgrad/km_data.json'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            km_data = json.loads(result.stdout)
            print(f"[OK] Git'ten {len(km_data)} tramvay okundu")
            
            # Veritabanındaki toplam Equipment sayısı
            total_equipment = Equipment.query.count()
            print(f"[INFO] Veritabanında {total_equipment} equipment var")
            
            # JSON verilerini yükle
            update_count = 0
            for tram_id, data in km_data.items():
                if not tram_id:  # Boş ID'yi atla
                    continue
                
                current_km = data.get('current_km', 0)
                
                # Veritabanında ara
                equipment = Equipment.query.filter_by(equipment_code=tram_id).first()
                
                if equipment:
                    old_km = equipment.current_km
                    equipment.current_km = current_km
                    print(f"  {tram_id}: {old_km:6d} -> {current_km:6d} km")
                    update_count += 1
                else:
                    print(f"  [WARN] {tram_id} veritabanında yok")
            
            # Değişiklikleri kaydet
            db.session.commit()
            print(f"\n[OK] {update_count} tramvay güncellendi")
            
            # JSON dosyasını da güncelle
            with open('./data/belgrad/km_data.json', 'w', encoding='utf-8') as f:
                json.dump(km_data, f, indent=2, ensure_ascii=False)
            print("[OK] km_data.json dosyası güncellendi")
            
        else:
            print(f"[ERROR] Git hatası: {result.stderr}")
