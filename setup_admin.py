"""
Admin kullanıcı oluştur veya doğrula
"""

from app import create_app, db
from models import User

app = create_app()

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        print(f"✓ Admin kullanıcı zaten var")
        print(f"  Username: {admin.username}")
        print(f"  Email: {admin.email}")
        print(f"  Role: {admin.role if hasattr(admin, 'role') else 'N/A'}")
    else:
        print("Admin kullanıcı oluşturuluyor...")
        admin = User(
            username='admin',
            email='admin@test.com',
            full_name='Admin User'
        )
        admin.set_password('admin123')
        if hasattr(admin, 'role'):
            admin.role = 'admin'
        db.session.add(admin)
        db.session.commit()
        print(f"✓ Admin kullanıcı oluşturuldu")
        print(f"  Username: admin")
        print(f"  Password: admin123")
        print(f"  Email: {admin.email}")

print("\n" + "=" * 60)
print("Login bilgileri:")
print("=" * 60)
print("Username: admin")
print("Password: admin123")
print("=" * 60)
