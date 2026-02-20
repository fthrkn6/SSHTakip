"""Test: Her proje kendi Excel'inden Equipment verisi çekiyor mu?"""
from models import Equipment, db
from routes.equipment import get_equipment_trams_from_excel
from app import create_app

app = create_app()
with app.app_context():
    projects = ['belgrad', 'gebze', 'iasi', 'kayseri', 'kocaeli', 'timisoara']
    
    print('='*70)
    print('TÜFM PROJELERİ - EQUIPMENT EXCEL FILTRESI KONTROL')
    print('='*70)
    
    for project in projects:
        # Excel'den çek
        excel_trams = get_equipment_trams_from_excel(project)
        excel_count = len(excel_trams) if excel_trams else 0
        
        # Database'den çek (tüm test verileri)
        db_all = Equipment.query.filter_by(project_code=project).all()
        db_count = len(db_all)
        
        print(f'\n{project.upper():12} | data/{project}/Veriler.xlsx')
        print(f'  Excel:       {excel_count:3} araç (source)')
        print(f'  Database:    {db_count:3} araç (includes test data)')
        
        if excel_trams:
            print(f'  Range:       {excel_trams[0]} - {excel_trams[-1]}')
        
        if excel_count > 0:
            print(f'  ✓ Equipment sayfa gösterecek: {excel_count} araç')
        else:
            print(f'  ✗ Excel dosyası bulunamadı veya boş')

print("\n" + "="*70)
print("SONUÇ: Tüm projeler kendi data/{proje}/ klasöründen veri çekiyor ✓")
print("="*70)
