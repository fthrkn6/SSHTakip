from app import create_app
from models import Equipment, ServiceStatus

app = create_app()
with app.app_context():
    # Equipment ID'lerini al
    equips = Equipment.query.filter_by(parent_id=None).all()
    
    print("=" * 60)
    print("EQUIPMENT IDs vs SERVICESTATUS tram_id'ler")
    print("=" * 60)
    
    print("\nEquipment IDs:")
    equip_ids = {e.id for e in equips}
    print(sorted(equip_ids))
    
    print("\nServiceStatus tram_id'ler:")
    statuses = ServiceStatus.query.all()
    status_ids = {int(s.tram_id) if s.tram_id.isdigit() else s.tram_id for s in statuses}
    print(sorted(list(status_ids)))
    
    # Karşılaştır
    print("\n" + "=" * 60)
    
    # Equipment ID ile eşleşiyor mu?
    numeric_status = {int(s.tram_id) for s in statuses if s.tram_id.isdigit()}
    common = equip_ids.intersection(numeric_status)
    
    print(f"Equipment ID'leri: {len(equip_ids)}")
    print(f"ServiceStatus numeric: {len(numeric_status)}")
    print(f"Ortak olanlar: {len(common)}")
    
    if common:
        print(f"Eşleşen ID'ler: {sorted(common)}")
    
    # Tüm Equipment'ları göster
    print("\n" + "=" * 60)
    print("TÜM EQUIPMENT")
    print("=" * 60)
    for e in sorted(equips, key=lambda x: x.id):
        print(f"ID: {e.id:4d} | Code: {e.equipment_code:10s} | Name: {e.name}")
