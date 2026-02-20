"""Bakım Planları sayfasında gösterilen verileri kontrol et"""
from models import Equipment, ServiceStatus, db
from routes.maintenance import load_trams_from_file
from app import create_app
from datetime import date

app = create_app()
with app.app_context():
    project = 'belgrad'
    
    # Maintenance sayfasında gösterilecek veri
    tram_ids = load_trams_from_file(project)
    
    print('BAKIM PLANLARI SAYFASINDA GÖSTERILEN VERİ')
    print('='*70)
    print(f'Excel\'den okunan araçlar: {len(tram_ids)}')
    print(f'Range: {tram_ids[0]} - {tram_ids[-1]}\n')
    
    # Equipment tablosundan al
    tramvaylar_equipment = Equipment.query.filter(
        Equipment.equipment_code.in_(tram_ids),
        Equipment.parent_id == None,
        Equipment.project_code == project
    ).order_by(Equipment.equipment_code).all()
    
    print(f'Equipment table\'dan çekilen: {len(tramvaylar_equipment)} araç')
    
    # Sayfada gösterilecek data
    today = str(date.today())
    tram_equipment_data = []
    
    for tramvay in tramvaylar_equipment:
        status_record = ServiceStatus.query.filter_by(
            tram_id=tramvay.equipment_code,
            date=today,
            project_code=project
        ).first()
        
        status_display = 'Servis'
        if status_record:
            status_display = status_record.status if status_record.status else 'Servis'
        
        tram_equipment_data.append({
            'tram_id': tramvay.equipment_code,
            'name': tramvay.name,
            'current_km': getattr(tramvay, 'current_km', 0),
            'total_km': getattr(tramvay, 'total_km', 0),
            'status': status_display
        })
    
    print(f'Sayfaya gönderilen data: {len(tram_equipment_data)} araç\n')
    
    # Sayfada gösterilecek verinin sonuna bak
    print('Son 5 araç:')
    print('-'*70)
    for data in tram_equipment_data[-5:]:
        print(f'{data["tram_id"]:6} | {data["name"]:18} | Status: {data["status"]}')
