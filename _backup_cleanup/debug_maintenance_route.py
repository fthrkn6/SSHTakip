"""Bakım Planları route'sinin tamamını debug et"""
from models import Equipment, ServiceStatus, db
from routes.maintenance import load_trams_from_file
from app import create_app
from datetime import date

app = create_app()
with app.app_context():
    project = 'belgrad'
    
    # 1. load_trams_from_file çıktısı
    tram_ids = load_trams_from_file(project)
    print(f"1. load_trams_from_file çıktısı: {len(tram_ids)} araç")
    print(f"   {tram_ids}")
    
    # 2. Equipment query
    equipment = Equipment.query.filter(
        Equipment.equipment_code.in_(tram_ids),
        Equipment.parent_id == None,
        Equipment.project_code == project
    ).order_by(Equipment.equipment_code).all()
    print(f"\n2. Equipment query: {len(equipment)} araç")
    for eq in equipment[-3:]:
        print(f"   {eq.equipment_code} | {eq.name}")
    
    # 3. tram_equipment_data oluşturma
    tram_equipment_data = []
    today = str(date.today())
    
    for tramvay in equipment:
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
            'current_km': tramvay.current_km if hasattr(tramvay, 'current_km') else 0,
            'total_km': tramvay.total_km if hasattr(tramvay, 'total_km') else 0,
            'status': status_display
        })
    
    print(f"\n3. tram_equipment_data oluşturuldu: {len(tram_equipment_data)} araç")
    for data in tram_equipment_data[-3:]:
        print(f"   {data['tram_id']} | {data['name']}")
    
    # 4. Template'e gönderilen veri
    print(f"\n4. render_template('maintenance/plans.html') gönderilen:")
    print(f"   - tram_equipment_data: {len(tram_equipment_data)} araç")
    print(f"   - plans: MaintenancePlan.query.filter(is_active=True, project_code={project})")
