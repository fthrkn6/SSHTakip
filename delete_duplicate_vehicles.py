#!/usr/bin/env python3
"""Yanlış formatlanmış araçları sil"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("🗑️  YANLIŞFORMATLANAN ARAÇLARI SİL")
    print("="*80)
    
    # Silinecek araçları bul
    wrong_format = Equipment.query.filter(
        Equipment.equipment_code.like('belgrad-%'),
        Equipment.project_code == 'belgrad',
        Equipment.parent_id == None
    ).all()
    
    print(f"\n❌ SİLİNECEK ARAÇLAR ({len(wrong_format)}):")
    print("\nBEFORE:")
    for eq in wrong_format[:5]:
        print(f"  - {eq.equipment_code}")
    if len(wrong_format) > 5:
        print(f"  ... ve {len(wrong_format)-5} daha")
    
    # SİL
    for eq in wrong_format:
        db.session.delete(eq)
    db.session.commit()
    
    print(f"\n✅ DELETED: {len(wrong_format)} araç silinidi")
    
    # SONRA
    remaining = Equipment.query.filter_by(
        project_code='belgrad',
        parent_id=None
    ).all()
    
    print(f"\nAFTER:")
    print(f"  Belgrad Equipment: {len(remaining)} araç")
    print(f"  Format: 1531, 1532, ..., 1555 ✅")
    
    print("\n" + "="*80)
    print("✅ SONUÇ: Database temizlendi")
    print("="*80 + "\n")
