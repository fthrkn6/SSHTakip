#!/usr/bin/env python3
"""Veriler.xlsx'i tamamen güncelle - Tüm 50 tram_id'yi ekle"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Equipment
import pandas as pd
import os

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("🔧 Veriler.xlsx GÜNCELLEME")
    print("="*80)
    
    # Belgrad'ın tüm equipment'lerini al
    belgrad_eq = Equipment.query.filter_by(
        project_code='belgrad',
        parent_id=None
    ).order_by(Equipment.equipment_code).all()
    
    print(f"\n1️⃣  Belgrad Equipment'leri")
    print(f"   Toplam: {len(belgrad_eq)}")
    
    # Tram ID'leri çıkar
    tram_ids = [eq.equipment_code for eq in belgrad_eq]
    print(f"   Tray ID'ler: {tram_ids[:5]}... ({len(tram_ids)} toplam)")
    
    # Excel dosyası oku
    veriler_file = 'data/belgrad/Veriler.xlsx'
    print(f"\n2️⃣  Excel Dosyası: {veriler_file}")
    print(f"   Okunuyor...")
    
    try:
        df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
        print(f"   Eski Veri: {len(df)} satır")
        print(f"   Sütunlar: {list(df.columns)}")
    except Exception as e:
        print(f"   Hata: {e}")
        sys.exit(1)
    
    # Yeni DataFrame oluştur
    print(f"\n3️⃣  Yeni DataFrame Oluşt")
    new_data = {'tram_id': tram_ids}
    
    # Eğer diğer sütunlar varsa kopyala
    if 'equipment_code' in df.columns:
        new_data['equipment_code'] = tram_ids
    
    new_df = pd.DataFrame(new_data)
    print(f"   Yeni Veri: {len(new_df)} satır")
    
    # Kaydet
    print(f"\n4️⃣  Dosya Kaydediliyor...")
    with pd.ExcelWriter(veriler_file, engine='openpyxl') as writer:
        new_df.to_excel(writer, sheet_name='Sayfa2', index=False)
    
    print(f"   ✅ Kaydedildi: {len(new_df)} tram_id")
    
    # Doğrulama
    print(f"\n5️⃣  Doğrulama")
    df_verify = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
    print(f"   Okunan veri: {len(df_verify)} satır")
    print(f"   İlk 5: {df_verify.head()['tram_id'].tolist()}")
    
    print("\n" + "="*80)
    print("✅ TAMAMLANDI - Oğan EN Veriler.xlsx güncellendi")
    print("="*80 + "\n")
