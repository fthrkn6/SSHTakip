#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
os.chdir(r'C:\Users\ferki\Desktop\bozankaya_ssh_takip')

from models import Equipment, ServiceStatus
from datetime import date
from tabulate import tabulate

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
    print("\n" + "="*100)
    print("🔍 DASHBOARD TRAMVAY FLEET - NEDİR ÇEKİLİYOR?")
    print("="*100 + "\n")
    
    # Equipment'ler
    tramvaylar = Equipment.query.filter_by(parent_id=None).all()
    today = str(date.today())
    service_status_records = ServiceStatus.query.filter_by(date=today).all()
    status_dict = {record.tram_id: record.status for record in service_status_records}
    
    # Tablosu
    table_data = []
    for tramvay in tramvaylar[:25]:  # İlk 25
        status_from_db = status_dict.get(tramvay.equipment_code, 'Servis')
        
        if status_from_db == 'Servis':
            status_display = 'aktif'
            badge = '🟢 Aktif'
        elif status_from_db == 'İşletme Kaynaklı Servis Dışı':
            status_display = 'bakim'
            badge = '🟠 Bakımda'
        else:
            status_display = 'ariza'
            badge = '🔴 Arızalı'
        
        table_data.append([
            tramvay.equipment_code,
            tramvay.name,
            tramvay.location if hasattr(tramvay, 'location') else '-',
            f"{tramvay.total_km if hasattr(tramvay, 'total_km') else 0:.0f} km",
            status_from_db,
            badge,
            status_display
        ])
    
    headers = ['Equipment Code', 'Name', 'Location', 'Total KM', 'Status (DB)', 'Badge', 'Status Display']
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    print(f"\n✅ Toplam Tramvay: {len(tramvaylar)}")
    print(f"✅ Bugün Servis Durumu Kaydı: {len(service_status_records)}")
    print(f"✅ Template'e Gönderilen: tramvay_statuses (list)\n")
    
    print("📊 DURUM ÖZETI:")
    aktif = sum(1 for t in table_data if t[5].startswith('🟢'))
    bakim = sum(1 for t in table_data if t[5].startswith('🟠'))
    ariza = sum(1 for t in table_data if t[5].startswith('🔴'))
    print(f"   🟢 Aktif (Servis): {aktif}")
    print(f"   🟠 Bakımda (İşletme): {bakim}")
    print(f"   🔴 Arızalı (Servis Dışı): {ariza}\n")
    
    print("="*100)
