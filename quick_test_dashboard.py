#!/usr/bin/env python
"""
Basit Dashboard Test Script
============================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from models import Equipment
from datetime import date

with app.app_context():
    # ======== KAYSERI ========
    print("\n" + "="*60)
    print("KAYSERI PROJESİ")
    print("="*60)
    
    kayseri_eq = Equipment.query.filter_by(
        parent_id=None,
        project_code='kayseri'
    ).all()
    
    print(f"\n✓ Toplam tramvay: {len(kayseri_eq)}")
    
    if kayseri_eq:
        # Status sayıları
        aktif = sum(1 for e in kayseri_eq if not e.status or e.status.lower() == 'aktif')
        ariza = sum(1 for e in kayseri_eq if e.status and 'ariza' in e.status.lower())
        isletme = sum(1 for e in kayseri_eq if e.status and 'isletme' in e.status.lower())
        
        print(f"✓ Aktif: {aktif}")
        print(f"✓ İşletme: {isletme}")
        print(f"✓ Arıza: {ariza}")
        
        total = len(kayseri_eq)
        availability = round((aktif + isletme) / total * 100, 1) if total > 0 else 0
        print(f"✓ Fleet Availability: {availability}%")
        
        print("\nİlk 5 tramvay:")
        for eq in kayseri_eq[:5]:
            print(f"  - {eq.equipment_code}: status='{eq.status}'")
    else:
        print("❌ Kayseri'de tramvay yok!")
    
    # ======== BELGRAD ========
    print("\n" + "="*60)
    print("BELGRAD PROJESİ")
    print("="*60)
    
    belgrad_eq = Equipment.query.filter_by(
        parent_id=None,
        project_code='belgrad'
    ).all()
    
    print(f"\n✓ Toplam tramvay: {len(belgrad_eq)}")
    
    if belgrad_eq:
        # Status sayıları
        aktif = sum(1 for e in belgrad_eq if not e.status or e.status.lower() == 'aktif')
        ariza = sum(1 for e in belgrad_eq if e.status and 'ariza' in e.status.lower())
        isletme = sum(1 for e in belgrad_eq if e.status and 'isletme' in e.status.lower())
        
        print(f"✓ Aktif: {aktif}")
        print(f"✓ İşletme: {isletme}")
        print(f"✓ Arıza: {ariza}")
        
        total = len(belgrad_eq)
        availability = round((aktif + isletme) / total * 100, 1) if total > 0 else 0
        print(f"✓ Fleet Availability: {availability}%")
        
        print("\nİlk 5 tramvay:")
        for eq in belgrad_eq[:5]:
            print(f"  - {eq.equipment_code}: status='{eq.status}'")
    else:
        print("❌ Belgrad'da tramvay yok!")
    
    print("\n" + "="*60)
    print("SONUÇ")
    print("="*60)
    if len(kayseri_eq) > 0 and len(belgrad_eq) > 0:
        print("\n✅ Tüm veriler mevcut - Dashboard çalışmalı")
    else:
        print("\n❌ HATA: Tramvay verisi eksik!")
        print("→ Equipment tablosuna data yüklenmeli")
        print("\nBaşlık: Kayseri ve Belgrad veri yönetimi")
        print("Adres: /equipment-management/bulk-import")
