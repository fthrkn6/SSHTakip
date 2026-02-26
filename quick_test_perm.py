"""Quick test for Permission table"""
from app import create_app, db
from models import Permission, RolePermission

app = create_app()
with app.app_context():
    print("[1] Creating tables...")
    db.create_all()
    
    print("[2] Checking existing permissions...")
    existing_count = db.session.query(Permission).count()
    print(f"    Existing permissions: {existing_count}")
    
    if existing_count == 0:
        print("[3] Adding sample permissions...")
        permissions_data = [
            {'page_name': 'dashboard', 'display_name': 'Dashboard'},
            {'page_name': 'ariza_listesi', 'display_name': 'Arıza Listesi'},
            {'page_name': 'yetkilendirme', 'display_name': 'Yetki Yönetimi'},
        ]
        
        for perm_data in permissions_data:
            p = Permission(**perm_data)
            db.session.add(p)
            print(f"    + {perm_data['display_name']}")
        
        db.session.commit()
        print("    ✓ Permissions added and committed")
    
    print("[4] Final check...")
    final_count = db.session.query(Permission).count()
    rp_count = db.session.query(RolePermission).count()
    print(f"    Permission count: {final_count}")
    print(f"    RolePermission count: {rp_count}")
    print("\n✓ Test completed successfully!")
