#!/usr/bin/env python3
"""Show exactly what Excel contains"""
import sys
sys.path.insert(0, '.')

from app import create_app
from utils.project_manager import ProjectManager
import pandas as pd

app = create_app()

with app.app_context():
    project = 'belgrad'
    
    print("\n" + "="*100)
    print("EXCEL VERISI - Tam Detay")
    print("="*100 + "\n")
    
    veriler_file = ProjectManager.get_veriler_file(project)
    print(f"File: {veriler_file}\n")
    
    # Sayfa2'yi oku
    df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
    
    print(f"1. Excel STRUKTUR:")
    print(f"   Toplam satir: {len(df)}")
    print(f"   Sutunlar: {list(df.columns)}\n")
    
    # Tum sutunlari goster
    print(f"2. SUTUN DETAYLARI:")
    for col in df.columns:
        print(f"   - {col}")
    print()
    
    # tram_id sutunu analiz et
    print(f"3. tram_id SUTUNU:")
    tram_id_values = df['tram_id'].dropna().tolist()
    unique_trams = sorted([str(t) for t in set(tram_id_values)])
    
    print(f"   Toplam deger: {len(tram_id_values)}")
    print(f"   Benzersiz: {len(unique_trams)}")
    print(f"   Min: {unique_trams[0]}, Max: {unique_trams[-1]}")
    print(f"   Degerler: {unique_trams}\n")
    
    # Eksik olanlar
    all_1531_to_1561 = [str(i) for i in range(1531, 1562)]
    missing = [t for t in all_1531_to_1561 if t not in unique_trams]
    extra = [t for t in unique_trams if t not in all_1531_to_1561]
    
    print(f"4. ANALIZ:")
    if missing:
        print(f"   Eksik (1531-1561 araliginda): {missing}")
    if extra:
        print(f"   Fazla/Diger: {extra}")
    
    # equipment_code sutunu kontrol et (varsa)
    if 'equipment_code' in df.columns:
        print(f"\n5. equipment_code SUTUNU:")
        equip_values = df['equipment_code'].dropna().tolist()
        unique_equip = sorted([str(t) for t in set(equip_values)])
        print(f"   Benzersiz: {len(unique_equip)}")
        print(f"   Degerler: {unique_equip[:10]}...")
    
    # Ilk 5 ve son 5 satir goster
    print(f"\n6. VERILER (Ilk 5 satir):")
    print(df[['tram_id'] + [col for col in df.columns if col != 'tram_id']].head(5).to_string())
    
    print(f"\n7. VERILER (Son 5 satir):")
    print(df[['tram_id'] + [col for col in df.columns if col != 'tram_id']].tail(5).to_string())
    
    print("\n" + "="*100 + "\n")
