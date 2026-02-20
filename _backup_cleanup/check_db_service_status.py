#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Veritabanında servis dışı kayıt kontrolü"""
import sys
sys.path.insert(0, '.')

from app import create_app
from models import ServiceStatus

app = create_app()

with app.app_context():
    print("=" * 70)
    print("VERITABANI KONTROL")
    print("=" * 70)
    
    # Tüm kayıtları say
    total = ServiceStatus.query.count()
    print(f"\nToplam ServiceStatus Kayitlari: {total}")
    
    # Servis Dışı kayıtları say
    out_of_service = ServiceStatus.query.filter(
        ServiceStatus.status.in_(['Servis Dışı', 'İşletme Kaynaklı Servis Dışı'])
    ).count()
    print(f"Servis Disi Kayitlari: {out_of_service}")
    
    if out_of_service == 0:
        print("\n!!! SAC! Veritabaninda servis disi kayit YOK!")
        print("\nRCA Raporu bos cikiyor cunku analiz edecek veri yok.")
        print("\nCozum: Once Servis Durumu sayfasinda veri girin")
        print("   1. Arac sec -> Tarih -> Sistem -> Alt Sistem -> Durum")
        print("   2. En az 5-10 kayit girin")
        print("   3. Sonra RCA raporunu deneyin")
    else:
        # Detay göster
        records = ServiceStatus.query.filter(
            ServiceStatus.status.in_(['Servis Dışı', 'İşletme Kaynaklı Servis Dışı'])
        ).order_by(ServiceStatus.date.desc()).limit(20).all()
        
        print(f"\nSon 20 Kayittan Ilkler:")
        for rec in records[:5]:
            sistema = rec.sistem or 'Belirtilmedi'
            alt_sistemid = rec.alt_sistem or 'Iceri'
            print(f"   * {rec.date} - {rec.tram_id} - {rec.status}")
            print(f"     Sistem: {sistema} / Alt Sistem: {alt_sistemid}")
    
    # Sistem dağılımı
    print(f"\nSistemler:")
    records = ServiceStatus.query.filter(
        ServiceStatus.status.in_(['Servis Dışı', 'İşletme Kaynaklı Servis Dışı'])
    ).all()
    
    if records:
        from collections import Counter
        sistemler = Counter(r.sistem or 'Belirtilmedi' for r in records)
        for sistem, count in sistemler.most_common(10):
            print(f"   * {sistem}: {count} kayit")
    
    print("\n" + "=" * 70)
