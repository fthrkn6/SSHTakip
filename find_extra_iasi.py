from app import app
from models import Equipment

with app.app_context():
    # İasi'deki tüm araçları list et
    iasi_eq = Equipment.query.filter_by(project_code='iasi').all()
    
    print(f"İasi'deki tüm {len(iasi_eq)} araç:")
    codes_sorted = sorted([int(eq.equipment_code) for eq in iasi_eq])
    print(codes_sorted)
    
    # 2217-2250'nin dışında neler var?
    excel_range = set(range(2217, 2251))  # 2217-2250
    db_codes = set(codes_sorted)
    
    extra = db_codes - excel_range
    missing = excel_range - db_codes
    
    print(f"\nExcel'de olması gereken ama Database'de olmayan: {sorted(missing)}")
    print(f"Database'de ama Excel'de olmayan (Extra): {sorted(extra)}")
