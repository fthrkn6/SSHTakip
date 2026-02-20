#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RCA rapor içeriğini kontrol"""
import sys
from datetime import datetime
sys.path.insert(0, '.')

from app import create_app
from utils_root_cause_analysis import RootCauseAnalyzer

app = create_app()

with app.app_context():
    print("=" * 70)
    print("RCA RAPOR ICERIGI KONTROL")
    print("=" * 70)
    
    # Test 1: Default tarih aralığı
    print("\n1. DEFAULT TARIH ARALIGI (90 gün geriye):")
    analysis1 = RootCauseAnalyzer.analyze_service_disruptions()
    print(f"   Start: {analysis1['start_date']}")
    print(f"   End: {analysis1['end_date']}")
    print(f"   Kayit Sayisi: {analysis1['total_records']}")
    
    # Bugünün tarihini al
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Test 2: Bugünü ve geçmişi kapsayan geniş aralık
    print(f"\n2. GENIS ARALLIK (2 ay - tum veriler):")
    analysis2 = RootCauseAnalyzer.analyze_service_disruptions(
        start_date='2026-01-16',
        end_date=today
    )
    print(f"   Start: {analysis2['start_date']}")
    print(f"   End: {analysis2['end_date']}")
    print(f"   Kayit Sayisi: {analysis2['total_records']}")
    
    if analysis2['total_records'] > 0:
        print(f"\n   Sistemler: {len(analysis2['sistem_analysis'])}")
        for sistem, data in analysis2['sistem_analysis'].items():
            print(f"   - {sistem}: {data['days']} gun, {data['count']} olay")
    
    # Test 3: Excel oluştur
    print(f"\n3. EXCEL RAPOR OLUSTUR:")
    if analysis2['total_records'] > 0:
        filepath = RootCauseAnalyzer.generate_rca_excel(analysis2)
        print(f"   Dosya: {filepath}")
        from pathlib import Path
        size = Path(filepath).stat().st_size / 1024
        print(f"   Boyut: {size:.1f} KB")
    else:
        print("   Hata: Kayit yok, rapor olusturulamadi")
    
    print("\n" + "=" * 70)
