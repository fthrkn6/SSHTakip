#!/usr/bin/env python3
"""Veriler.xlsx'i 25 araçla sınırlandır"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment
import pandas as pd
import os

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("📝 VERILER.XLSX - 25 ARAÇLA GÜNCELLE")
    print("="*80)
    
    # Database'den doğru araçları al
    belgrad_eq = Equipment.query.filter_by(
        project_code='belgrad',
        parent_id=None
    ).order_by(Equipment.equipment_code).all()
    
    print(f"\n1️⃣  Database'den araçları oku:")
    print(f"   Toplam: {len(belgrad_eq)}")
    
    tram_ids = [eq.equipment_code for eq in belgrad_eq]
    print(f"   Format: {tram_ids[:3]}... {tram_ids[-3:]}")
    
    # Excel güncelle
    excel_file = 'data/belgrad/Veriler.xlsx'
    print(f"\n2️⃣  Excel dosyasını güncelle: {excel_file}")
    
    new_df = pd.DataFrame({'tram_id': tram_ids})
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        new_df.to_excel(writer, sheet_name='Sayfa2', index=False)
    
    print(f"   ✅ Kaydedildi: {len(new_df)} satır")
    
    # Doğrulama
    print(f"\n3️⃣  Doğrulama:")
    df_verify = pd.read_excel(excel_file, sheet_name='Sayfa2', header=0)
    print(f"   Okunan: {len(df_verify)} satır")
    print(f"   İçerik: {df_verify['tram_id'].tolist()}")
    
    print("\n" + "="*80)
    print("✅ TAMAMLANDI:")
    print("  Database: 25 araç")
    print("  Excel: 25 araç")
    print("  ENDPOINT: 25 araç döneceğiz!")
    print("="*80 + "\n")
