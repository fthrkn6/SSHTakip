from app import create_app
from models import ServiceLog, db

app = create_app()
with app.app_context():
    # TRV-* kayıtlarını sil
    logs_to_delete = ServiceLog.query.filter(ServiceLog.tram_id.like('TRV-%')).all()
    
    print(f"Silinecek TRV-* kayıtları: {len(logs_to_delete)}")
    for log in logs_to_delete:
        print(f"  ✗ {log.tram_id} - {log.new_status} ({log.log_date})")
    
    if logs_to_delete:
        for log in logs_to_delete:
            db.session.delete(log)
        db.session.commit()
        print(f"\n✅ {len(logs_to_delete)} kayıt silindi")
    else:
        print("Silinecek kayıt yok")
