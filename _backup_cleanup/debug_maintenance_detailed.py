"""Bakım Planları tram_equipment_data sayısını kontrol et"""
from models import Equipment, ServiceStatus, MaintenancePlan, db
from routes.maintenance import load_trams_from_file
from app import create_app
from datetime import date
from flask import session

app = create_app()

# Session simulasyonu
with app.test_request_context():
    from flask import session as flask_session
    
    # Simulate session
    with app.app_context():
        project = 'belgrad'
        
        print('BAKIM PLANLARI ROUTE KONTROLÜ')
        print('='*70)
        print(f'Session project: {project}\n')
        
        # 1. tram_ids
        tram_ids = load_trams_from_file(project)
        print(f'1. load_trams_from_file({project}):')
        print(f'   Dönen araç sayısı: {len(tram_ids)}')
        print(f'   Araçlar: {tram_ids}\n')
        
        # 2. Equipment query
        equipment = Equipment.query.filter(
            Equipment.equipment_code.in_(tram_ids),
            Equipment.parent_id == None,
            Equipment.project_code == project
        ).order_by(Equipment.equipment_code).all()
        
        print(f'2. Equipment query result:')
        print(f'   Equipment sayısı: {len(equipment)}')
        print(f'   Son 3: {[eq.equipment_code for eq in equipment[-3:]]}\n')
        
        # 3. tram_equipment_data dict'i oluştur
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
        
        print(f'3. tram_equipment_data dict:')
        print(f'   Dict sayısı: {len(tram_equipment_data)}')
        print(f'   Son 3: {[d["tram_id"] for d in tram_equipment_data[-3:]]}\n')
        
        # 4. Template header'da gösterilecek sayı
        print(f'4. Template header\'da görülecek:')
        print(f'   {{ tram_equipment_data|length }} = {len(tram_equipment_data)} araç')
        
        # 5. Bakım planları
        plans = MaintenancePlan.query.filter_by(
            is_active=True,
            project_code=project
        ).order_by(MaintenancePlan.plan_name).all()
        
        print(f'\n5. Bakım Planları:')
        print(f'   Aktif plan sayısı: {len(plans)}')
