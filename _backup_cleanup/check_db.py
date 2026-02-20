from app import create_app
from models import ServiceLog, ServiceStatus

app = create_app()
with app.app_context():
    service_log_count = ServiceLog.query.count()
    service_status_count = ServiceStatus.query.count()
    
    print('=' * 50)
    print('DATABASE VERİ SAYILARI')
    print('=' * 50)
    print(f'\nServiceLog (service_logs): {service_log_count} kayıt')
    print(f'ServiceStatus (service_status): {service_status_count} kayıt')
    
    if service_log_count > 0:
        print('\n--- ServiceLog Örnekleri (Son 3) ---')
        logs = ServiceLog.query.order_by(ServiceLog.log_date.desc()).limit(3).all()
        for log in logs:
            print(f'  {log.tram_id} - {log.new_status} ({log.log_date.strftime("%Y-%m-%d %H:%M")})')
            print(f'    Reason: {log.reason}')
            print(f'    Sistem: {log.sistem}, Alt Sistem: {log.alt_sistem}')
    
    if service_status_count > 0:
        print('\n--- ServiceStatus Örnekleri (Son 3) ---')
        statuses = ServiceStatus.query.order_by(ServiceStatus.updated_at.desc()).limit(3).all()
        for status in statuses:
            print(f'  {status.tram_id} - {status.status} ({status.date})')
            print(f'    Açıklama: {status.aciklama}')
            print(f'    Sistem: {status.sistem}')
    
    print('\n' + '=' * 50)
