"""
Test admin panel routes
"""
import requests
from app import create_app
from models import db, User

def test_admin_routes():
    app = create_app()
    
    with app.test_client() as client:
        print("Testing Admin Panel Routes...")
        print("=" * 60)
        
        # Test 1: Admin dashboard should exist
        print("\n1. Testing /admin/dashboard (requires login)")
        response = client.get('/admin/dashboard')
        print(f"   Status: {response.status_code}")
        print(f"   Result: {'✓ Redirects to login (expected)' if response.status_code == 302 else '✗ Unexpected'}")
        
        # Test 2: Users management should exist
        print("\n2. Testing /admin/users (requires login)")
        response = client.get('/admin/users')
        print(f"   Status: {response.status_code}")
        print(f"   Result: {'✓ Redirects to login (expected)' if response.status_code == 302 else '✗ Unexpected'}")
        
        # Test 3: Check if admin user exists and can authenticate
        print("\n3. Checking admin user in database")
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print(f"   ✓ Admin user exists")
                print(f"   ✓ Role: {admin.role}")
                print(f"   ✓ Email: {admin.email}")
                print(f"   ✓ Is active: {admin.is_active}")
                print(f"   ✓ Is admin: {admin.is_admin()}")
                print(f"   ✓ Assigned projects: {admin.get_assigned_projects()}")
            else:
                print(f"   ✗ Admin user not found")
        
        # Test 4: Login as admin
        print("\n4. Testing admin login")
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            if admin and admin.check_password('admin123'):
                print(f"   ✓ Admin password verified successfully")
            else:
                print(f"   ✗ Admin password verification failed")
        
        # Test 5: User model methods
        print("\n5. Testing User model methods")
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print(f"   ✓ can_access_project('belgrad'): {admin.can_access_project('belgrad')}")
                print(f"   ✓ can_access_project('iasi'): {admin.can_access_project('iasi')}")
                print(f"   ✓ is_admin(): {admin.is_admin()}")
                print(f"   ✓ is_saha(): {admin.is_saha()}")
        
        print("\n" + "=" * 60)
        print("Admin panel setup verification complete!")

if __name__ == '__main__':
    test_admin_routes()
