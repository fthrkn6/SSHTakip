from app import app
from utils_project_excel_store import get_tramvay_list_with_km

with app.app_context():
    # Kayseri için get_tramvay_list_with_km test et
    eqs = get_tramvay_list_with_km('kayseri')
    
    print(f"Kayseri get_tramvay_list_with_km sonucu: {len(eqs)} araç")
    for eq in eqs:
        print(f"  {eq.equipment_code}")
    
    # 4001 var mı?
    codes = [eq.equipment_code for eq in eqs]
    if '4001' in codes or 4001 in codes:
        print("\n✗ 4001 hala görülüyor!")
    else:
        print("\n✓ 4001 yok - temiz!")
