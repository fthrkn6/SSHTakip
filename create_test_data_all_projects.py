"""
Tüm Projeler İçin Test Verisi Oluşturma Script'i
Excel Grid Dosyalarını Doldura ve RCA Verisi Ekle
"""

import pandas as pd
from datetime import datetime, timedelta
from utils_excel_grid_manager import ExcelGridManager, RCAExcelManager
import os
import sys

# Projeler
PROJECTS = [
    'belgrad',
    'istanbul',
    'ankara',
    'iasi',
    'timisoara',
    'kayseri',
    'kocaeli',
    'gebze',
    'samsun',
]

# Test Araçları (Her proje için)
TEST_EQUIPMENT = {
    'belgrad': ['1531', '1532', '1533', '1534', '1535'],
    'istanbul': ['T101', 'T102', 'T103', 'T104', 'T105'],
    'ankara': ['A001', 'A002', 'A003', 'A004', 'A005'],
    'iasi': ['I001', 'I002', 'I003'],
    'timisoara': ['TIM001', 'TIM002', 'TIM003'],
    'kayseri': ['K001', 'K002', 'K003'],
    'kocaeli': ['KOC001', 'KOC002', 'KOC003'],
    'gebze': ['G001', 'G002', 'G003'],
    'samsun': ['S001', 'S002', 'S003'],
}

# Sistem/Alt sistem kombinasyonları
RCA_SYSTEMS = {
    'BRAKE': ['Kaliper', 'Piston', 'Fren Hortumu', 'Balata'],
    'ENGINE': ['Yakıt Sistemi', 'Motor Bloğu', 'Silindir Kapağı', 'Enjektör'],
    'TRANSMISSION': ['Vites Kutusu', 'Debriyaj', 'Tork Dönüştürücü'],
    'ELECTRICAL': ['Alternator', 'Starter', 'Batarya', 'Kablolama'],
    'SUSPENSION': ['Amortisör', 'Yay', 'Aks', 'Lastik'],
    'HVAC': ['Kompresör', 'Condenser', 'Blower Motor', 'Soğutkan'],
}

def create_test_data():
    """Test verilerini tüm projeler için oluştur"""
    
    # Get app root path
    app_root = os.path.dirname(os.path.abspath(__file__))
    
    for project_code in PROJECTS:
        print(f"\n{'='*60}")
        print(f"📊 Proje: {project_code.upper()}")
        print(f"{'='*60}")
        
        equipment_codes = TEST_EQUIPMENT.get(project_code, [])
        
        if not equipment_codes:
            print(f"⚠️  {project_code} için test araçları bulunamadı")
            continue
        
        # 1. Excel Grid Files İnit Et
        print(f"✓ Excel Grid dosyası oluşturuluyor...")
        grid_manager = ExcelGridManager(project_code)
        grid_path = grid_manager.init_grid(app_root, equipment_codes)
        print(f"  ✅ Grid oluşturuldu: {grid_path}")
        
        # 2. Test Verisi Ekle (Batch - Optimized)
        print(f"✓ Durum verileri ekleniyor (toplu)...")
        today = datetime.now().date()
        updates = []
        
        for day_offset in range(7):  # Son 7 gün (optimize)
            current_date = (today - timedelta(days=day_offset)).strftime('%Y-%m-%d')
            
            for equipment_id in equipment_codes:
                import random
                status = random.choices(
                    ['aktif', 'servis_disi', 'isletme_kaynakli'],
                    weights=[70, 20, 10]
                )[0]
                
                updates.append({
                    'tram_id': equipment_id,
                    'date': current_date,
                    'status': status
                })
        
        # Batch güncelleme (tek dosya açma/kapama)
        if updates:
            grid_manager.batch_update_status(app_root, updates)
            print(f"  ✅ {len(updates)} durum kaydı eklendi")
        
        # 3. RCA Excel Files İnit Et
        print(f"✓ RCA Excel dosyası oluşturuluyor...")
        rca_manager = RCAExcelManager(project_code)
        rca_path = rca_manager.init_rca(app_root)
        print(f"  ✅ RCA dosyası oluşturuldu: {rca_path}")
        
        # 4. RCA Test Verileri Ekle (Daha az - optimize)
        print(f"✓ RCA verileri ekleniyor...")
        rca_count = 0
        
        for day_offset in range(7):  # Son 7 gün
            current_date = (today - timedelta(days=day_offset))
            
            # Her gün 1-2 arıza ekle (optimize)
            import random
            ariza_sayisi = random.randint(1, 2)
            
            for _ in range(ariza_sayisi):
                equipment_id = random.choice(equipment_codes)
                system = random.choice(list(RCA_SYSTEMS.keys()))
                subsystem = random.choice(RCA_SYSTEMS[system])
                category = random.choices(
                    ['servis_disi', 'isletme_kaynakli'],
                    weights=[70, 30]
                )[0]
                description = f"Test arızası - {category}"
                
                rca_manager.add_rca_record(
                    app_root,
                    equipment_id,
                    system,
                    subsystem,
                    category,
                    description
                )
                rca_count += 1
        
        print(f"  ✅ {rca_count} RCA kaydı eklendi")
        
        # İstatistikler
        system_stats = rca_manager.get_system_stats(app_root)
        subsystem_stats = rca_manager.get_subsystem_stats(app_root)
        
        print(f"\n📈 İstatistikler:")
        print(f"  Sistem arızaları: {dict(list(system_stats.items())[:5])}")
        print(f"  Alt sistem arızaları: {dict(list(subsystem_stats.items())[:5])}")


if __name__ == '__main__':
    try:
        print("\n🚀 Tüm Projeler İçin Test Verisi Oluşturuluyor...\n")
        create_test_data()
        print(f"\n{'='*60}")
        print("✅ TEST VERİSİ BAŞARIYLA OLUŞTURULDU!")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"\n❌ HATA: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
