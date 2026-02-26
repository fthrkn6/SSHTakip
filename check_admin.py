from app import create_app, db
from models import User

app = create_app()
with app.app_context():
    print("[1] Checking tojson filter...")
    if 'tojson' in app.jinja_env.filters:
        print("    ✓ tojson filter exists")
    else:
        print("    ✗ tojson filter NOT found")
    
    print("\n[2] Checking admin user...")
    admin = User.query.filter_by(role='admin').first()
    if admin:
        print(f"    ✓ Admin found:")
        print(f"      - username: {admin.username}")
        print(f"      - role: '{admin.role}'")
        print(f"      - is_admin(): {admin.is_admin()}")
    else:
        print("    ✗ No admin user found")
    
    print("\n[3] All users:")
    users = User.query.all()
    for user in users[:10]:
        print(f"    - {user.username}: role='{user.role}' (is_admin: {user.is_admin()})")
