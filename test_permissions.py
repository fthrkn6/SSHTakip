"""Test Permission models"""
import sys
sys.path.insert(0, '.')

try:
    from app import create_app, db
    print("✓ create_app ve db import OK")
    
    from models import Permission, RolePermission
    print("✓ Permission, RolePermission import OK")
    
    app = create_app()
    print("✓ create_app() OK")
    
    with app.app_context():
        print("✓ app_context OK")
        
        # Test query
        count = db.session.query(Permission).count()
        print(f"✓ Permission tablosu query OK - {count} kayıt")
        
        rp_count = db.session.query(RolePermission).count()
        print(f"✓ RolePermission tablosu query OK - {rp_count} kayıt")
        
        if count == 0:
            print("\n⚠ Permission tablosu boş! init_permissions.py çalıştır")
        else:
            print("\n✓ Permission tablolarında veriler var!")
            
except Exception as e:
    print(f"✗ HATA: {e}")
    import traceback
    traceback.print_exc()
