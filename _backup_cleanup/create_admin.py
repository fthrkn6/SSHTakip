"""
Create admin user for testing
"""
from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print('✓ Admin user already exists')
        print(f'  Username: admin')
        print(f'  Role: {admin.role}')
    else:
        # Create admin user
        admin = User(
            username='admin',
            email='admin@bozankaya.com',
            full_name='System Administrator',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        admin.set_assigned_projects(['*'])
        
        db.session.add(admin)
        db.session.commit()
        print('✓ Admin user created successfully')
        print(f'  Username: admin')
        print(f'  Password: admin123')
        print(f'  Email: admin@bozankaya.com')
        print(f'  Role: admin')
        print(f'  Assigned Projects: All (*)')
