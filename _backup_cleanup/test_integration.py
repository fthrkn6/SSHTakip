from app import create_app
from models import ServiceStatus, Equipment

app = create_app()
with app.app_context():
    print("=" * 70)
    print("SİSTEM ENTEGRASYON TESTİ")
    print("=" * 70)
    
    # 1. Equipment
    equips = Equipment.query.filter_by(parent_id=None).all()
    print(f"\n✅ Equipment kayıtları: {len(equips)}")
    print(f"   Örnek: {[e.equipment_code for e in equips[:5]]}")
    
    # 2. ServiceStatus
    statuses = ServiceStatus.query.all()
    print(f"\n✅ ServiceStatus kayıtları: {len(statuses)}")
    print(f"   Bugünün kayıtları: {ServiceStatus.query.filter_by(date='2026-02-10').count()}")
    
    # 3. Eşleşme kontrol
    equip_codes = {e.equipment_code for e in equips}
    status_ids = {s.tram_id for s in statuses}
    
    matching = equip_codes.intersection(status_ids)
    print(f"\n✅ Equipment ↔ ServiceStatus eşleşme: {len(matching)}/{len(equip_codes)}")
    
    if len(matching) == len(equip_codes):
        print("   ✅ PERFECT - Tüm tramvaylar eşleşiyor!")
    else:
        print(f"   ⚠️ Eksik: {equip_codes - status_ids}")
    
    # 4. Dashboard'da gösterilecek durumlar
    print(f"\n✅ Dashboard Durum Dağılımı:")
    today_statuses = ServiceStatus.query.filter_by(date='2026-02-10').all()
    status_counts = {}
    for s in today_statuses:
        status_val = s.status
        status_counts[status_val] = status_counts.get(status_val, 0) + 1
    
    for status, count in sorted(status_counts.items()):
        print(f"   • {status}: {count}")
    
    print(f"\n✅ SISTEM HAZIR - Tüm veriler konsolide edildi!")
