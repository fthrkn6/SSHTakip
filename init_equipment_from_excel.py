#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Equipment tablosunu Veriler.xlsx'ten başlat
Sadece doğru 25 araç (1531-1555)
"""
import sys
sys.path.insert(0, '.')

from app import create_app
from models import Equipment, db
import pandas as pd
import os

app = create_app()

with app.app_context():
    project_code = 'belgrad'
    
    print("="*70)
    print("Equipment Tablosu Baslatiliyor")
    print("="*70)
    
    # 1. Veriler.xlsx'ten araclari oku
    print("\n[1] Veriler.xlsx'ten araclari oku:")
    veriler_file = os.path.join('data', project_code, 'Veriler.xlsx')
    df = pd.read_excel(veriler_file, sheet_name='Sayfa2')
    tram_ids = [str(int(t)) for t in df['tram_id'].dropna().unique()]
    print(f"    Bulundu: {len(tram_ids)} arac")
    print(f"    Araclar: {sorted(tram_ids)}")
    
    # 2. km_data.xlsx'ten KM degerlerini oku
    print("\n[2] km_data.xlsx'ten KM degerlerini oku:")
    km_file = os.path.join('data', project_code, 'km_data.xlsx')
    df_km = pd.read_excel(km_file)
    km_map = {str(row['tram_id']): {
        'current_km': int(row['current_km']) if row['current_km'] else 0,
        'notes': str(row.get('notes', '')) or ''
    } for _, row in df_km.iterrows()}
    print(f"    KM verileri yuklendi: {len(km_map)} arac")
    
    # 3. Equipment tablosu doldur
    print("\n[3] Equipment tablosu doldurulmasi:")
    created = 0
    for tram_id in sorted(tram_ids):
        # Zaten var mı kontrol et
        existing = Equipment.query.filter_by(
            equipment_code=tram_id,
            project_code=project_code
        ).first()
        
        if existing:
            print(f"    [EXISTS] {tram_id}: Already exists")
            continue
        
        # KM degeri varsa al, yoksa 0
        km_info = km_map.get(tram_id, {})
        current_km = km_info.get('current_km', 0)
        notes = km_info.get('notes', '')
        
        # Yeni Equipment olustur
        eq = Equipment(
            equipment_code=tram_id,
            name=f'Tramvay {tram_id}',
            equipment_type='Tramvay',
            current_km=current_km,
            monthly_km=0,
            notes=notes,
            project_code=project_code
        )
        db.session.add(eq)
        created += 1
        print(f"    [OK] {tram_id}: {current_km} km")
    
    # Kaydet
    if created > 0:
        db.session.commit()
        print(f"\n[OK] {created} arac Equipment tablosuna eklendi")
    else:
        print(f"\n[INFO] Yeni arac eklenmedi (zaten doldurmus olabilir)")
    
    # 4. Dogrulama
    print("\n[4] Dogrulama:")
    equipments = Equipment.query.filter_by(project_code=project_code, equipment_type='Tramvay').all()
    total_km = sum(e.current_km or 0 for e in equipments)
    print(f"    Toplam Equipment: {len(equipments)}")
    print(f"    Toplam KM: {total_km}")
    
    if len(equipments) == len(tram_ids):
        print(f"    [OK] BASARILI: Equipment tablosu KM verilerine hazir!")
    else:
        print(f"    [WARNING] Arac sayisi uyusmyor!")
    
    print("\n" + "="*70)
    print("SONRAKI ADIM:")
    print("  1. /tramvay-km sayfasini ac")
    print("  2. KM degerleri gir ve kaydet")
    print("  3. /bakim-planlari sayfasinda degerleri gor (otomatik senkronizasyon)")
    print("="*70)
