from app import app, db
from models import Equipment

with app.app_context():
    # İasi araçlarını kontrol et
    iasi_eq = Equipment.query.filter_by(project_code='iasi').limit(5).all()
    
    print(f"İasi'deki Equipment sayısı: {Equipment.query.filter_by(project_code='iasi').count()}")
    print(f"\nİlk 5:")
    for eq in iasi_eq:
        print(f"  {eq.equipment_code} -> project: {eq.project_code}")
    
    # Tüm project codes neler?
    all_projects = db.session.query(Equipment.project_code).distinct().all()
    print(f"\nTüm project codes Database'de:")
    for proj in all_projects:
        count = Equipment.query.filter_by(project_code=proj[0]).count()
        print(f"  {proj[0]}: {count}")
