#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
os.chdir(r'C:\Users\ferki\Desktop\bozankaya_ssh_takip')

from models import ServiceStatus
from datetime import date
import collections

# Flask uygulamasını yükle
def create_app():
    from flask import Flask
    from models import db
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ssh_takip_bozankaya.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

app = create_app()

with app.app_context():
    today = str(date.today())
    records = ServiceStatus.query.filter_by(date=today).all()
    
    print(f"\n📊 ServiceStatus Verileri - Bugün ({today}):\n")
    print(f"Toplam Araç Sayısı: {len(records)}\n")
    
    if records:
        # Durum sayıları
        status_count = collections.Counter([r.status for r in records])
        print("Durum Dağılımı:")
        for status, count in sorted(status_count.items()):
            print(f"  • {status}: {count}")
        
        print(f"\nDetaylı Liste (ilk 15):")
        for r in records[:15]:
            print(f"  {r.tram_id}: {r.status}")
        
        if len(records) > 15:
            print(f"  ... ve {len(records) - 15} tane daha")
    else:
        print("⚠️ Bugün için veri bulunamadı!")
