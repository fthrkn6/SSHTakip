import os
import pandas as pd

print("=" * 70)
print("SISTEM VERİ KAYNAĞI ANALİZİ")
print("=" * 70)

# 1. Veriler.xlsx'deki tram_id'ler
print("\n1. VERİLER.XLSX SAYFA2 - TRAM_ID SÜTUNU")
print("-" * 70)
veriler_path = "data/belgrad/Veriler.xlsx"
df = pd.read_excel(veriler_path, sheet_name='Sayfa2')
tram_ids = df['tram_id'].dropna().unique().tolist()
print(f"Toplam tramvay: {len(tram_ids)}")
print(f"Tramvay ID'leri: {sorted(tram_ids)}")

# 2. Equipment tablosuna bakma
print("\n2. DATABASE - EQUIPMENT TABLOSU")
print("-" * 70)
from app import create_app
from models import Equipment

app = create_app()
with app.app_context():
    equips = Equipment.query.filter_by(parent_id=None).all()
    print(f"Toplam Equipment: {len(equips)}")
    
    equip_codes = set()
    for e in equips:
        equip_codes.add(e.equipment_code)
    
    equip_codes_sorted = sorted([c for c in equip_codes if c and len(str(c)) <= 10])
    print(f"Equipment codes (ilk 15): {equip_codes_sorted[:15]}")
    
    # Veriler.xlsx'deki tram_id'ler ile Equipment code eşleşiyor mu?
    print("\n3. UYUMLULUK KONTROLÜ")
    print("-" * 70)
    
    tram_ids_str = [str(int(t)) for t in tram_ids]
    common = set(tram_ids_str).intersection(equip_codes)
    
    print(f"Veriler.xlsx tram_id'ler: {len(tram_ids_str)} adet")
    print(f"Equipment codes: {len(equip_codes)} adet")
    print(f"Ortak olanlar: {len(common)} adet")
    
    if len(common) == len(tram_ids_str):
        print(f"\n✅ UYUMLU - Tüm tramvay ID'leri eşleşiyor!")
        print(f"Veriler.xlsx'teki tüm tram_id'ler Equipment'ta kayıtlı")
    else:
        print(f"\n❌ UYUMSUZLUK BULUNDU")
        print(f"Sadece Veriler.xlsx'te: {set(tram_ids_str) - equip_codes}")
        print(f"Sadece Equipment'ta: {equip_codes - set(tram_ids_str)}")

# 3. ServiceStatus'te neler var?
print("\n4. SERVICESTATUS TABLOSU")
print("-" * 70)
with app.app_context():
    from models import ServiceStatus
    statuses = ServiceStatus.query.all()
    status_ids = {s.tram_id for s in statuses}
    
    print(f"Toplam ServiceStatus kaydı: {len(status_ids)} adet")
    print(f"ServiceStatus tram_id'leri (ilk 15): {sorted(list(status_ids))[:15]}")
    
    # Veriler.xlsx ile eşleşiyor mu?
    status_ids_set = set(str(int(s)) if str(s).isdigit() else s for s in status_ids)
    common_status = status_ids_set.intersection(set(tram_ids_str))
    
    print(f"\nVeriler.xlsx ile ServiceStatus arasında ortak: {len(common_status)}")
    if len(common_status) == len(tram_ids_str):
        print("✅ Tüm tramvaylar ServiceStatus'ta var")
    else:
        print(f"❌ Eksik olanlar: {set(tram_ids_str) - common_status}")
