#!/usr/bin/env python3
"""PROJE İZOLASYONU ANALİZİ - Her proje kendi dosyasından veri çekiyor mu?"""
import sys
sys.path.insert(0, '.')

from app import create_app
import os

app = create_app()

print("\n" + "="*120)
print("📋 PROJE İZOLASYONU KONTROLÜ")
print("="*120 + "\n")

print("1️⃣  EXCEL DOSYA YAPISI (Her proje kendi dosya olmalı)")
print("-" * 120)

# Data klasörünü kontrol et
data_dir = os.path.join(app.root_path, 'data')
if os.path.exists(data_dir):
    projects = os.listdir(data_dir)
    projects = [p for p in projects if os.path.isdir(os.path.join(data_dir, p))]
    
    print(f"Bulunan Projeler: {projects}\n")
    
    for project in projects:
        project_dir = os.path.join(data_dir, project)
        veriler_file = os.path.join(project_dir, 'Veriler.xlsx')
        
        if os.path.exists(veriler_file):
            size = os.path.getsize(veriler_file) / 1024  # KB
            print(f"  ✅ {project}/Veriler.xlsx ({size:.1f} KB)")
        else:
            print(f"  ❌ {project}/Veriler.xlsx YOKSUN")
else:
    print("❌ data/ klasörü bulunamadı")

print("\n2️⃣  ROUTES KOD ANALİZİ - project_code filtresi kontrol")
print("-" * 120)

# Önemli route'ları kontrol et
routes_to_check = [
    'routes/dashboard.py',
    'routes/service_status.py',
    'routes/maintenance.py',
    'routes/reports.py',
]

import re

for route_file in routes_to_check:
    full_path = os.path.join(app.root_path, route_file)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # project_code filtre kontrolü
        has_filter = 'project_code' in content
        has_session = "session.get('current_project'" in content or 'session.get("current_project"' in content
        
        print(f"\n  📄 {route_file}")
        print(f"     {'✅' if has_filter else '❌'} project_code filtresi: {has_filter}")
        print(f"     {'✅' if has_session else '❌'} session'dan project alıyor: {has_session}")
        
        # Queries kontrolü
        if 'Equipment.query' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'Equipment.query' in line and 'filter' in lines[min(i+5, len(lines)-1)]:
                    # Sonraki 5 satırda filter var mı kontrol et
                    next_lines = '\n'.join(lines[i:i+6])
                    if 'project_code' in next_lines:
                        print(f"     ✅ Equipment sorguları project_code ile filtreleniyor")
                        break

print("\n3️⃣  DATABASE MODELLERİ - project_code alanları kontrol")
print("-" * 120)

with app.app_context():
    from models import Equipment, ServiceStatus, MaintenancePlan
    
    # Equipment
    eq_cols = [f"  - {col}" for col in Equipment.__table__.columns.keys() if 'project' in col.lower()]
    print("  Equipment table:")
    for col in eq_cols:
        print(col)
    
    # ServiceStatus
    ss_cols = [f"  - {col}" for col in ServiceStatus.__table__.columns.keys() if 'project' in col.lower()]
    print("\n  ServiceStatus table:")
    for col in ss_cols:
        print(col)
    
    # MaintenancePlan
    if hasattr(MaintenancePlan, '__table__'):
        mp_cols = [f"  - {col}" for col in MaintenancePlan.__table__.columns.keys() if 'project' in col.lower()]
        print("\n  MaintenancePlan table:")
        for col in mp_cols:
            print(col)

print("\n4️⃣  ÖRNEK VERİ - Farklı projelerin veri ayrımı")
print("-" * 120)

with app.app_context():
    from models import Equipment
    
    # Proje kodlarını bul
    all_equipment = Equipment.query.all()
    projects_in_db = list(set([eq.project_code for eq in all_equipment]))
    
    print(f"Database'deki Projeler: {projects_in_db}")
    
    for project in projects_in_db:
        count = Equipment.query.filter_by(project_code=project, parent_id=None).count()
        print(f"  - {project}: {count} araç")

print("\n5️⃣  SENKRONIZASYON TAVSIYESI")
print("-" * 120)
print("""
Her proje için senkronizasyon stratejisi:

├─ belgrad/ klasörü
│  └─ Veriler.xlsx (25-26 araç)
│     → Equipment table (project_code='belgrad')
│     → ServiceStatus table (project_code='belgrad')
│
├─ ankara/ klasörü
│  └─ Veriler.xlsx (X araç)
│     → Equipment table (project_code='ankara')
│     → ServiceStatus table (project_code='ankara')
│
└─ Other Projeler
   └─ Veriler.xlsx
      → Equipment table (project_code=...)
      → ServiceStatus table (project_code=...)

Önemli Noktalar:
✅ Session'dan current_project alın
✅ Tüm queries'lere project_code filtresi ekleyin
✅ Excel dosyası her zaman: data/{project_code}/Veriler.xlsx
✅ Frontend'de proje seçimi yapıldığında session güncelle
✅ API endpoints'leri project_code parametresiyle başlasın
""")

print("="*120 + "\n")
