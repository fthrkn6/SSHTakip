#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RCA testi için test veri ekle"""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, '.')

from app import create_app
from models import ServiceStatus, db

app = create_app()

with app.app_context():
    print("=" * 70)
    print("TEST VERI EKLEME")
    print("=" * 70)
    
    # Test verisi
    test_data = [
        ('1531', '2026-02-16', 'Servis Disi', 'Battery', 'Batarya Hucreleri', 'Batarya guclu degil'),
        ('1531', '2026-02-15', 'Servis Disi', 'Battery', 'Batarya Hucreleri', 'Batarya guclu degil'),
        ('1531', '2026-02-14', 'Servis Disi', 'Battery', 'Sarj Devreleri', 'Sarj devresinde sorun'),
        ('1532', '2026-02-16', 'Servis Disi', 'Engine', 'Motor Blogu', 'Motor astar bozuk'),
        ('1532', '2026-02-15', 'Servis Disi', 'Engine', 'Motor Blogu', 'Motor astar bozuk'),
        ('1533', '2026-02-14', 'Isletme Kaynaklı Servis Disi', 'Hydraulics', 'Hidrolik sivisi', 'Hidrolik sivisi bos'),
        ('1533', '2026-02-13', 'Isletme Kaynaklı Servis Disi', 'Hydraulics', 'Pompalar', 'Pompa ses cikariyor'),
        ('1534', '2026-02-16', 'Servis Disi', 'Electrical', 'Kablolama', 'Kablo koptu'),
        ('1534', '2026-02-15', 'Servis Disi', 'Electrical', 'Sigortalar', 'Sigorta yanmis'),
        ('1535', '2026-02-14', 'Servis Disi', 'Brakes', 'Fren Padi', 'Fren padi yipranmis'),
        ('1535', '2026-02-13', 'Servis Disi', 'Brakes', 'Fren Sivisi', 'Fren sivisi bos'),
        ('1536', '2026-02-12', 'Isletme Kaynaklı Servis Disi', 'Transmission', 'Vitesler', 'Vites kaymasi var'),
        ('1537', '2026-02-16', 'Servis Disi', 'Suspension', 'Yaylar', 'Yay kirildi'),
        ('1537', '2026-02-11', 'Servis Disi', 'Suspension', 'Amortisörler', 'Amortisör satildi'),
    ]
    
    added = 0
    skipped = 0
    
    for tram_id, date, status, sistem, alt_sistem, aciklama in test_data:
        # Zaten var mı kontrol et
        existing = ServiceStatus.query.filter_by(
            tram_id=tram_id,
            date=date
        ).first()
        
        if existing:
            skipped += 1
            print(f"   (-) {date} - {tram_id} - Zaten var")
        else:
            record = ServiceStatus(
                tram_id=tram_id,
                date=date,
                status=status,
                sistem=sistem,
                alt_sistem=alt_sistem,
                aciklama=aciklama
            )
            db.session.add(record)
            added += 1
            print(f"   (+) {date} - {tram_id} - {sistem} / {alt_sistem} eklendi")
    
    db.session.commit()
    
    print("\n" + "=" * 70)
    print(f"SONUC: {added} veri eklendi, {skipped} var zaten")
    
    # Kontrol
    total = ServiceStatus.query.filter(
        ServiceStatus.status.in_(['Servis Disi', 'Isletme Kaynaklı Servis Disi'])
    ).count()
    print(f"Toplam Servis Disi: {total} kayit")
    
    print("\nArtik RCA Raporunuz dolu olacak!")
    print("=" * 70)
