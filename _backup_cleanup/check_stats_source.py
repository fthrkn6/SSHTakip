"""
ServiceStatus Tablosu Veri Kaynağı Kontrolü
==========================================
"""

from models import ServiceStatus, Equipment
from datetime import date
from flask import session
import os
import pandas as pd

# Bugünün tarihi
today = str(date.today())
print(f"Bugün: {today}")

# Aktif proje
current_project = 'kayseri'  # Kayseri örneği
print(f"\nProje: {current_project}")

# ============================================================
# 1. ServiceStatus verileri kontrolü
# ============================================================
print("\n" + "="*60)
print("1. ServiceStatus TABLOSU ANALİZİ")
print("="*60)

# Bugünün kaç kaydı var?
today_records = ServiceStatus.query.filter_by(date=today).all()
print(f"\nBugün ({today}) ServiceStatus kaydı: {len(today_records)}")

# Proje bazında
filtered_records = [r for r in today_records if hasattr(r, 'project_code') and r.project_code == current_project]
print(f"Kayseri'de bugün: {len(filtered_records)}")

# Durum dağılımı
print("\nDurum Dağılımı:")
for r in today_records[:10]:
    print(f"  - {r.tram_id}: {r.status if r.status else 'Durum yok'}")
if len(today_records) > 10:
    print(f"  ... ({len(today_records)-10} daha)")

# ============================================================
# 2. Equipment tablosu kontrolü
# ============================================================
print("\n" + "="*60)
print("2. EQUIPMENT TABLOSU ANALİZİ")
print("="*60)

# Proje bazında tramvaylar
project_equipment = Equipment.query.filter_by(
    parent_id=None,
    project_code=current_project
).all()
print(f"\nKayseri'de toplam Equipment: {len(project_equipment)}")

# Hangileri ServiceStatus'te?
equipment_codes = [eq.equipment_code for eq in project_equipment]
has_status = []
no_status = []

for code in equipment_codes:
    status = ServiceStatus.query.filter_by(
        tram_id=code,
        date=today
    ).first()
    if status:
        has_status.append(code)
    else:
        no_status.append(code)

print(f"ServiceStatus kaydı olan: {len(has_status)}")
print(f"ServiceStatus kaydı olmayan (DEFAULT 'aktif'): {len(no_status)}")

if no_status:
    print(f"\nKaydı olmayan tramvaylar (otomatik AKTIF sayılacak):")
    for code in no_status[:5]:
        print(f"  - {code}")
    if len(no_status) > 5:
        print(f"  ... ({len(no_status)-5} daha)")

# ============================================================
# 3. Veriler.xlsx kontrol
# ============================================================
print("\n" + "="*60)
print("3. VERİLER.XLSX ANALİZİ")
print("="*60)

veriler_file = f'data/{current_project}/Veriler.xlsx'
if os.path.exists(veriler_file):
    try:
        df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
        
        # Tram ID sütununu bul
        tram_id_col = None
        for col in df.columns:
            if 'tram' in col.lower() or 'equipment' in col.lower():
                tram_id_col = col
                break
        
        if tram_id_col:
            tram_ids = df[tram_id_col].dropna().unique().tolist()
            print(f"\nVeriler.xlsx'te tanımlanmış tram_id'ler: {len(tram_ids)}")
            for tid in tram_ids[:5]:
                print(f"  - {tid}")
            if len(tram_ids) > 5:
                print(f"  ... ({len(tram_ids)-5} daha)")
            
            # Kaç tanesinin ServiceStatus kaydı var?
            with_status = sum(1 for t in tram_ids if ServiceStatus.query.filter_by(tram_id=str(t), date=today).first())
            without_status = len(tram_ids) - with_status
            
            print(f"\nVeriler.xlsx'te ServiceStatus kaydı olan: {with_status}")
            print(f"Veriler.xlsx'te ServiceStatus kaydı OLMAYAN: {without_status} (→ AKTIF sayılır)")
    except Exception as e:
        print(f"Hata: {e}")
else:
    print(f"\nVeriler.xlsx bulunamadı: {veriler_file}")

# ============================================================
# 4. Hesaplama Kontrolü
# ============================================================
print("\n" + "="*60)
print("4. STATS HESAPLAMASı KONTROLÜ")
print("="*60)

aktif_count = 0
isletme_count = 0
ariza_count = 0

# Bugün der kaydı
for r in today_records:
    status_value = r.status if r.status else 'Servis'
    
    if 'İşletme' in status_value:
        isletme_count += 1
    elif 'Dışı' in status_value:
        ariza_count += 1
    else:
        aktif_count += 1

# +ServiceStatus kaydı olmayan (otomatik aktif)
aktif_count += len(no_status)

print(f"\nServiceStatus kaydından:")
print(f"  Aktif (db + kayıt yok): {aktif_count} = {len(has_status) - isletme_count - ariza_count} + {len(no_status)}")
print(f"  İşletme Kaynaklı: {isletme_count}")
print(f"  Arızalı: {ariza_count}")
print(f"  Toplam: {aktif_count + isletme_count + ariza_count}")

total = aktif_count + isletme_count + ariza_count
kullanilabilir = aktif_count + isletme_count
availability = round(kullanilabilir / total * 100, 1) if total > 0 else 0

print(f"\nFilo Kullanılabilirlik: ({aktif_count} + {isletme_count}) / {total} * 100 = {availability}%")

# ============================================================
# 5. SONUÇ
# ============================================================
print("\n" + "="*60)
print("SONUÇ VE ÖNERİLER")
print("="*60)

if len(no_status) > 0:
    uyari_orani = (len(no_status) / len(equipment_codes) * 100) if equipment_codes else 0
    print(f"\n⚠️ DİKKAT: {uyari_orani:.1f}% tramvayın ServiceStatus kaydı yok!")
    print("→ Bu tramvaylar otomatik AKTIF sayılıyor")
    print("→ ServiceStatus tablosu düzenli güncellenmeli")
else:
    print(f"\n✅ Tüm tramvayların ServiceStatus kaydı var")

if len(has_status) == 0:
    print("\n❌ HATA: Bugün için hiç ServiceStatus kaydı yok!")
    print("→ Stats verisi YANLIŞ olacak")
    print("→ ServiceStatus'i güncellemek gerekiyor")
