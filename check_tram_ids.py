from app import create_app
from models import ServiceLog, ServiceStatus

app = create_app()
with app.app_context():
    # ServiceLog tram_id'lerini al
    service_log_ids = set()
    logs = ServiceLog.query.all()
    for log in logs:
        service_log_ids.add(log.tram_id)
    
    # ServiceStatus tram_id'lerini al
    service_status_ids = set()
    statuses = ServiceStatus.query.all()
    for status in statuses:
        service_status_ids.add(status.tram_id)
    
    print("=" * 60)
    print("SERVICELOG TRAM_ID'ler")
    print("=" * 60)
    print(f"Toplam: {len(service_log_ids)}")
    print(sorted(service_log_ids))
    
    print("\n" + "=" * 60)
    print("SERVICESTATUS TRAM_ID'ler")
    print("=" * 60)
    print(f"Toplam: {len(service_status_ids)}")
    print(sorted(service_status_ids))
    
    print("\n" + "=" * 60)
    print("HER İKİSİNDE DE OLAN TRAM_ID'ler")
    print("=" * 60)
    both = service_log_ids.intersection(service_status_ids)
    print(f"Toplam: {len(both)}")
    print(sorted(both) if both else "HİÇ BİR ORTAK ID YOK!")
    
    print("\n" + "=" * 60)
    print("SADECE SERVICELOG'TA OLAN")
    print("=" * 60)
    only_log = service_log_ids - service_status_ids
    print(f"Toplam: {len(only_log)}")
    print(sorted(only_log))
    
    print("\n" + "=" * 60)
    print("SADECE SERVICESTATUS'TA OLAN")
    print("=" * 60)
    only_status = service_status_ids - service_log_ids
    print(f"Toplam: {len(only_status)}")
    print(sorted(only_status))
