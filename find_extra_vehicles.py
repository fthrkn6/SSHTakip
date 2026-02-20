#!/usr/bin/env python3
"""Son 25 araç nereden geldi - kontrol et"""
import sys
sys.path.insert(0, '.')

from app import create_app
from models import Equipment

app = create_app()

with app.app_context():
    # İLK 25 ARAÇ
    first_25 = Equipment.query.filter_by(
        project_code='belgrad', 
        parent_id=None
    ).order_by(Equipment.equipment_code).limit(25).all()
    
    print("\n" + "="*80)
    print("🔍 ARAÇ KAYNAĞINI KONTROL ET")
    print("="*80)
    
    print("\n1️⃣  İLK 25 ARAÇ (tram_id format):\n")
    for i, eq in enumerate(first_25, 1):
        print(f"   {i:2d}. {eq.equipment_code:10s} -> {eq.name}")
    
    # SON 25 ARAÇ
    last_25 = Equipment.query.filter_by(
        project_code='belgrad', 
        parent_id=None
    ).order_by(Equipment.equipment_code.desc()).limit(25).all()
    
    print("\n2️⃣  SON 25 ARAÇ (belgrad- format):\n")
    for i, eq in enumerate(reversed(last_25), 1):
        print(f"   {i:2d}. {eq.equipment_code:10s} -> {eq.name}")
    
    print("\n3️⃣  SORUN HATALI FORMATLAMA:\n")
    print("   - İlk 25: 1531, 1532, ... (Doğru format)")
    print("   - Son 25: belgrad-1551, belgrad-1552, ... (YANLIŞ format!)")  
    print(f"\n   ❌ İKİ FARKLI FORMAT = VERI KARŞAŞTIRMASI!")
    
    print("\n4️⃣  VERİ KAYNAĞINI BULMA:\n")
    print("   activate_all_projects_fixed.py satır 69:")
    print("   → status='aktif' ile Equipment eklendi")
    print("   → format: equipment_code = str(tram_id)")
    print("\n   İkincidir ??? BENİ NE SCRIPT EKLEDI?")
    
    print("\n" + "="*80)
    print("✅ CÖZÜM:")
    print("="*80)
    print("""
SEÇENEK 1: Son 25 araçı sil (Database)
  DROP WHERE equipment_code LIKE 'belgrad-%'
  
SEÇENEK 2: Son 25 araçları düzelt (format değiştir)
  UPDATE equipment 
  SET equipment_code = REPLACE(equipment_code, 'belgrad-', '')
  WHERE project_code='belgrad'

SEÇENEK 3: Excel'i temizle ve sadece ilk 25'i tut
  Veriler.xlsx → sadece 1531-1555
""")
    print("="*80 + "\n")
