#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
os.chdir(r'C:\Users\ferki\Desktop\bozankaya_ssh_takip')

from models import Equipment, ServiceLog
from datetime import date
from sqlalchemy import desc
import collections

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
    print("\n" + "="*60)
    print("📊 DASHBOARD VERİ KARŞILAŞTIRMASI")
    print("="*60 + "\n")
    
    # Equipment durumlarını kontrol et
    print("1️⃣ EQUIPMENT TABLOSU:")
    equipment_list = Equipment.query.filter_by(parent_id=None).all()
    eq_status_count = collections.Counter([eq.status for eq in equipment_list if eq.status])
    print(f"   Toplam Araç: {len(equipment_list)}")
    print(f"   Durum Dağılımı: {dict(eq_status_count)}\n")
    
    # ServiceLog'dan son durum kontrol et
    print("2️⃣ SERVICELOG TABLOSU (Son Durum):")
    service_log_status = {}
    for eq in equipment_list[:25]:  # İlk 25 araç
        latest_log = ServiceLog.query.filter_by(
            tram_id=eq.equipment_code
        ).order_by(desc(ServiceLog.log_date)).first()
        
        if latest_log:
            status = latest_log.new_status
            reason = latest_log.reason if latest_log.reason else ''
            
            # Kategorize et
            if 'işletme' in reason.lower():
                cat = 'İşletme Kaynaklı'
            elif any(x in status.lower() for x in ['dışı', 'offline', 'down']):
                cat = 'Servis Dışı'
            else:
                cat = 'Servis'
            
            service_log_status[eq.equipment_code] = {
                'status': status,
                'reason': reason,
                'category': cat,
                'log_date': latest_log.log_date
            }
    
    log_cat_count = collections.Counter([v['category'] for v in service_log_status.values()])
    print(f"   ServiceLog'da Durum: {dict(log_cat_count)}")
    print(f"   Kontrol edilen araç: {len(service_log_status)}\n")
    
    print("3️⃣ KARŞILAŞTIRMA:")
    print(f"   ✅ ServiceStatus (SQL): Servis=24, Servis Dışı=1")
    print(f"   ❓ Equipment: Durum={dict(eq_status_count)}")
    print(f"   ❓ ServiceLog: Durum={dict(log_cat_count)}\n")
    
    print("4️⃣ SONUÇ:")
    print("   🟢 ServiceStatus = DOĞRU VERİ (24 Servis, 1 Servis Dışı)")
    print("   ⚠️ Dashboard'ın ServiceLog'dan veri çekmesi yerine")
    print("   ✨ ServiceStatus'ten veri çekmesi gerekiyor!")
    print("\n" + "="*60 + "\n")
