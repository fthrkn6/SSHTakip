"""
Equipment Status Kontrol Script
================================
Dashboard'da stats kullanılan Equipment.status değerlerini kontrol et
"""

from models import Equipment
from flask import session
import pandas as pd

print("="*70)
print("EQUIPMENT STATUS KONROL")
print("="*70)

# Belgrad
print("\n📍 BELGRAD")
print("-"*70)
belgrad_eq = Equipment.query.filter_by(
    parent_id=None,
    project_code='belgrad'
).all()

print(f"Toplam: {len(belgrad_eq)}")

# Status dağılımı
status_counts = {}
for eq in belgrad_eq:
    status = eq.status if eq.status else 'NULL'
    status_counts[status] = status_counts.get(status, 0) + 1
    
print("\nStatus Dağılımı:")
for status, count in status_counts.items():
    print(f"  {status}: {count}")

# Örnekler
print("\nİlk 10 Tramvay:")
for eq in belgrad_eq[:10]:
    print(f"  {eq.equipment_code}: status='{eq.status}'")

# Kayseri
print("\n" + "="*70)
print("📍 KAYSERI")
print("-"*70)
kayseri_eq = Equipment.query.filter_by(
    parent_id=None,
    project_code='kayseri'
).all()

print(f"Toplam: {len(kayseri_eq)}")

# Status dağılımı
status_counts = {}
for eq in kayseri_eq:
    status = eq.status if eq.status else 'NULL'
    status_counts[status] = status_counts.get(status, 0) + 1
    
print("\nStatus Dağılımı:")
for status, count in status_counts.items():
    print(f"  {status}: {count}")

# Örnekler
print("\nİlk 10 Tramvay:")
for eq in kayseri_eq[:10]:
    print(f"  {eq.equipment_code}: status='{eq.status}'")

# ============================================================
# SONUÇ
# ============================================================
print("\n" + "="*70)
print("ÖNEMLİ NOTLAR")
print("="*70)

if len(belgrad_eq) == 0 or len(kayseri_eq) == 0:
    print("\n❌ HATA: Equipment tablosu proje verisi içermiyor!")
    print("→ Dashboard tramvay listesi boş olacak")

# Status değerlerini kontrol et
valid_statuses = ['aktif', 'bakim', 'ariza', 'servis_disi']
invalid_statuses = set()

for eq in belgrad_eq + kayseri_eq:
    if eq.status and eq.status.lower() not in valid_statuses:
        invalid_statuses.add(eq.status)

if invalid_statuses:
    print(f"\n⚠️ DİKKAT: Geçersiz status değerleri:")
    for status in invalid_statuses:
        print(f"  - '{status}'")
    print("\n→ Dashboard'daki status sınıflandırması yanlış olabilir")
    print("→ Status değerlerini şu şekilde normalizasyon yapılması gerekiyor:")
    print("  'aktif', 'bakim', 'ariza', 'servis_disi'")
else:
    print("\n✅ Tüm status değerleri geçerli")

print("\n" + "="*70)
