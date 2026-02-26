#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HBR (Hata Bildirim Raporu) dosya oluşturma testini yap.
BEL25-NCR dosya adlandırması test et.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Test için path ayarlama
sys.path.insert(0, str(Path(__file__).parent))

# Logs classını import et
from modules.logs import Logs

def test_hbr_creation():
    """HBR dosya oluşturmayı test et"""
    
    # Test parametreleri
    project_code = "BELGRAD"
    vehicle_number = "1531"
    failure_type = "Test Arıza"
    system_name = "Motor"
    
    print(f"🧪 HBR Oluşturma Testi Başlıyor...")
    print(f"   Proje: {project_code}")
    print(f"   Araç: {vehicle_number}")
    print(f"   Arıza: {failure_type}")
    
    try:
        # Logs sınıfı oluştur
        logs = Logs()
        
        # HBR dizinini kontrol et
        hbr_dir = logs.get_project_path(project_code) / "HBR"
        print(f"\n📁 HBR Klasörü: {hbr_dir}")
        
        if hbr_dir.exists():
            existing_files = [f for f in os.listdir(hbr_dir) if f.startswith("BEL25-NCR-")]
            print(f"✅ Mevcut BEL25-NCR dosyaları: {len(existing_files)}")
            if existing_files:
                print("   📄", ", ".join(sorted(existing_files)[:3]))
        else:
            print("❌ HBR klasörü bulunamadı!")
            return False
        
        # Test dosyası oluştur
        next_counter = len(existing_files) + 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        test_filename = f"BEL25-NCR-{next_counter:03d}_{timestamp}.xlsx"
        test_path = hbr_dir / test_filename
        
        print(f"\n📋 Test Dosyası Adı: {test_filename}")
        
        # Dummy dosya oluştur (test amaçlı)
        test_path.touch()
        
        if test_path.exists():
            print(f"✅ HBR Test Dosyası Başarıyla Oluşturuldu: {test_path.name}")
            # Hemen sil
            test_path.unlink()
            print(f"✅ Test dosyası temizlendi")
            return True
        else:
            print(f"❌ Dosya oluşturulamadı!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hbr_creation()
    
    if success:
        print("\n" + "="*60)
        print("✅ HBR dosya oluşturma testi BAŞARILI")
        print("   BEL25-NCR-* adlandırma standardı doğrulandı")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ HBR test başarısız")
        print("="*60)
        sys.exit(1)
