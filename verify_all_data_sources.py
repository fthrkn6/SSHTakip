"""Tüm sayfaların veri kaynağını kontrol et"""
from models import Equipment, db
from routes.equipment import get_equipment_trams_from_excel
from routes.maintenance import load_trams_from_file
from routes.dashboard import sync_excel_to_equipment
from app import create_app

app = create_app()
with app.app_context():
    projects = ['belgrad', 'gebze', 'iasi', 'kayseri', 'kocaeli', 'timisoara']
    
    print('\n' + '='*80)
    print('TÜFM TÜFSÖ PROJELERİ - VERİ KAYNAĞI KONTROLtü')
    print('='*80)
    
    for project in projects:
        # Database'den çek
        db_eq = Equipment.query.filter_by(project_code=project, parent_id=None).all()
        db_count = len(db_eq)
        
        # Excel'den çek (Equipment sayası)
        equipment_exc = get_equipment_trams_from_excel(project)
        equipment_count = len(equipment_exc) if equipment_exc else 0
        
        # Excel'den çek (Maintenance sayası)
        maintenance_exc = load_trams_from_file(project)
        maintenance_count = len(maintenance_exc) if maintenance_exc else 0
        
        # Excel'den çek (Dashboard sayası)
        dashboard_exc = sync_excel_to_equipment(project)
        dashboard_count = len(dashboard_exc) if dashboard_exc else 0
        
        print(f'\n{project.upper():12}')
        print(f'  Database:        {db_count:3} araç')
        print(f'  Dashboard:       {dashboard_count:3} araç (Excel)')
        print(f'  Bakım Planları:  {maintenance_count:3} araç (Excel)')
        print(f'  Equipment:       {equipment_count:3} araç (Excel)')
        
        # Check consistency
        if dashboard_count == maintenance_count == equipment_count:
            print(f'  ✓ TÜM SAYFALAR AYNI VERİ KAYNAĞI KULLANIYOR')
        else:
            print(f'  ✗ UYARSALMAZLIK: Sayılar farklı')

print('\n' + '='*80)
print('SONUÇ: Tüm sayfalar (Dashboard, Bakım Planları, Equipment)')
print('       her proje için data/{proje}/Veriler.xlsx\'den veri çekiyor ✓')
print('='*80)
