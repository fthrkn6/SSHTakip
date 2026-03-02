from app import app
from utils_project_excel_store import get_tramvay_list_with_km

with app.app_context():
    # İasi için get_tramvay_list_with_km test et
    eqs = get_tramvay_list_with_km('iasi')
    
    print(f"İasi get_tramvay_list_with_km sonucu: {len(eqs)} araç")
    codes = [eq.equipment_code for eq in eqs]
    print(f"Equipment codes: {codes}")
    
    # 2001-2017 var mı?
    orphan_found = [c for c in codes if c.startswith('200') and int(c) < 2018]
    
    if orphan_found:
        print(f"\n✗ Hala orphan var: {orphan_found}")
    else:
        print(f"\n✓ 2001-2017 tamamen silindi!")
