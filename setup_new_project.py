"""
YENİ PROJE EKLEME REHBERI
========================

1. KLASÖR OLUŞTUR
   data/{proje_adi}/

2. GEREKLİ DOSYALAR
   ✓ Veriler.xlsx - Excel dosyası (Sayfa2 sayfası gerekli - araç kodları)
   ✓ maintenance.json - Bakım planı JSON (bakım KM seviyeleri)
   ✓ fracas.xlsx (opsiyonel) - Arıza kayıtları

3. Excel YAPISI (Veriler.xlsx)
   Sheet Name: "Sayfa2"
   Column A: Araç Kodları (2217, 2218, 2219, ...)
   Column B: Araç Adı (opsiyonel)
   ...

4. MAINTENANCE.JSON YAPISI
   {
     "15K": {"km": 15000, "works": ["BOZ-001"]},
     "30K": {"km": 30000, "works": ["BOZ-002"]},
     ...
   }

5. DATABASE KAYDETME
   - Otomatik: get_tramvay_list_with_km() Excel'den okuyor
   - API çağrısında sync_equipment_with_excel() Database'ye yazıyor

6. HABERLEŞ
   - Admin panel: Yeni projeler otomatik görünecek
   - ProjectManager sınıfı kullanılıyor
"""

import os
import json
import shutil

def create_new_project(project_name, vehicle_codes=None, maintenance_template=None):
    """
    Yeni proje oluştur
    
    Args:
        project_name: Proje adı (belgrad, iasi, vb.)
        vehicle_codes: Araç kodları listesi (opsiyonel)
        maintenance_template: Bakım şablonu (opsiyonel)
    """
    
    project_path = f'data/{project_name}'
    
    # 1. Klasör oluştur
    if os.path.exists(project_path):
        print(f"✗ {project_name} klasörü zaten var!")
        return False
    
    os.makedirs(project_path, exist_ok=True)
    print(f"✓ Klasör oluşturuldu: {project_path}")
    
    # 2. maintenance.json oluştur
    if maintenance_template is None:
        maintenance_template = {
            "15K": {"km": 15000, "works": ["BOZ-001"]},
            "30K": {"km": 30000, "works": ["BOZ-002"]},
            "60K": {"km": 60000, "works": ["BOZ-003", "BOZ-004"]},
            "90K": {"km": 90000, "works": ["BOZ-005"]},
            "120K": {"km": 120000, "works": ["BOZ-006", "BOZ-007"]},
            "200K": {"km": 200000, "works": ["BOZ-008"]}
        }
    
    maintenance_path = os.path.join(project_path, 'maintenance.json')
    with open(maintenance_path, 'w', encoding='utf-8') as f:
        json.dump(maintenance_template, f, indent=2, ensure_ascii=False)
    print(f"✓ maintenance.json oluşturuldu")
    
    # 3. Veriler.xlsx oluştur (template)
    excel_path = os.path.join(project_path, 'Veriler.xlsx')
    
    try:
        import pandas as pd
        
        # Sayfa2 oluştur
        if vehicle_codes is None:
            vehicle_codes = [1001, 1002, 1003]  # Örnek
        
        df = pd.DataFrame({
            'Araç Kodu': vehicle_codes,
            'Araç Adı': [f'Araç {code}' for code in vehicle_codes]
        })
        
        # Excel'e yaz (Sayfa2)
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sayfa2', index=False)
        
        print(f"✓ Veriler.xlsx oluşturuldu ({len(vehicle_codes)} araç)")
    
    except ImportError:
        print(f"⚠ Pandas yüklü değil - Excel dosyasını manuel oluştur")
        print(f"  Path: {excel_path}")
    
    # 4. Bilgi dosyası
    info_path = os.path.join(project_path, 'README.md')
    with open(info_path, 'w', encoding='utf-8') as f:
        f.write(f"""# {project_name.upper()} PROJESİ

## Dosyalar
- **Veriler.xlsx**: Araç listesi (Sayfa2)
- **maintenance.json**: Bakım planı
- **fracas.xlsx**: Arıza kayıtları (opsiyonel)
- **km_data.json**: KM geçmişi (opsiyonel)

## Yapı
- Araç Kodları: Column A (Sayfa2)
- Bakım Seviyeleri: 15K, 30K, 60K, 90K, 120K, 200K

## Senkronizasyon
- Database otomatik Excel'le senkronize olur
- Her API çağrısında kontrol edilir
""")
    
    print(f"✓ README.md oluşturuldu")
    print(f"\n✅ Proje '{project_name}' oluşturuldu!")
    print(f"Lokasyon: {os.path.abspath(project_path)}")
    
    return True

if __name__ == '__main__':
    print("=== YENİ PROJE OLUŞTUR ===\n")
    
    # Örnek: ANKARA projesi oluştur
    ankara_vehicles = [5001, 5002, 5003, 5004, 5005]
    
    create_new_project(
        project_name='ankara',
        vehicle_codes=ankara_vehicles
    )
