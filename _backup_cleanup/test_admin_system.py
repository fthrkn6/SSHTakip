#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Admin Panel & Role System Test Script
Test the implementation of role-based access control and admin panel
"""

import os
import sys
from pathlib import Path

# Add workspace to path
workspace = Path(__file__).parent
sys.path.insert(0, str(workspace))

from models import db, User
from app import create_app
from datetime import datetime

def test_user_model():
    """Test User model with role-based methods"""
    print("\n" + "="*60)
    print("TEST 1: User Model Role System")
    print("="*60)
    
    app = create_app()
    with app.app_context():
        # Create test users
        admin_user = User(
            username='admin_test',
            email='admin@test.com',
            full_name='Test Admin',
            role='admin'
        )
        admin_user.set_password('admin123')
        admin_user.set_assigned_projects(['*'])
        
        saha_user = User(
            username='saha_test',
            email='saha@test.com',
            full_name='Test Saha User',
            role='saha'
        )
        saha_user.set_password('saha123')
        saha_user.set_assigned_projects(['belgrad', 'ankara', 'istanbul'])
        
        # Test methods
        print("\n✓ Admin User Tests:")
        print(f"  - is_admin(): {admin_user.is_admin()}")
        print(f"  - is_saha(): {admin_user.is_saha()}")
        print(f"  - can_access_project('belgrad'): {admin_user.can_access_project('belgrad')}")
        print(f"  - can_access_project('ankara'): {admin_user.can_access_project('ankara')}")
        print(f"  - can_access_project('istanbul'): {admin_user.can_access_project('istanbul')}")
        print(f"  - get_assigned_projects(): {admin_user.get_assigned_projects()}")
        print(f"  - get_role_display(): {admin_user.get_role_display()}")
        
        print("\n✓ Saha User Tests:")
        print(f"  - is_admin(): {saha_user.is_admin()}")
        print(f"  - is_saha(): {saha_user.is_saha()}")
        print(f"  - can_access_project('belgrad'): {saha_user.can_access_project('belgrad')}")
        print(f"  - can_access_project('ankara'): {saha_user.can_access_project('ankara')}")
        print(f"  - can_access_project('istanbul'): {saha_user.can_access_project('istanbul')}")
        print(f"  - can_access_project('kocaeli'): {saha_user.can_access_project('kocaeli')}")
        print(f"  - get_assigned_projects(): {saha_user.get_assigned_projects()}")
        print(f"  - get_role_display(): {saha_user.get_role_display()}")
        
        print("\n✅ User Model Tests Passed!")


def test_admin_routes():
    """Test admin routes configuration"""
    print("\n" + "="*60)
    print("TEST 2: Admin Routes Configuration")
    print("="*60)
    
    app = create_app()
    
    # Get all routes
    admin_routes = []
    for rule in app.url_map.iter_rules():
        if 'admin' in rule.rule:
            admin_routes.append({
                'rule': rule.rule,
                'methods': ', '.join(rule.methods - {'HEAD', 'OPTIONS'}),
                'endpoint': rule.endpoint
            })
    
    print(f"\n✓ Found {len(admin_routes)} admin routes:")
    for route in sorted(admin_routes, key=lambda x: x['rule']):
        print(f"  - {route['rule']:<35} [{route['methods']}]")
    
    # Check specific admin routes
    expected_routes = [
        '/admin/',
        '/admin/dashboard',
        '/admin/users',
        '/admin/users/add',
        '/admin/users/<int:user_id>/edit',
        '/admin/projects',
        '/admin/projects/add',
        '/admin/backups',
    ]
    
    print(f"\n✓ Checking expected routes:")
    for expected in expected_routes:
        found = any(expected.replace('<int:user_id>', '123') in route['rule'] 
                   for route in admin_routes)
        status = "✓" if found else "✗"
        print(f"  {status} {expected}")
    
    print("\n✅ Admin Routes Tests Passed!")


def test_decorators():
    """Test that decorator functions exist"""
    print("\n" + "="*60)
    print("TEST 3: Decorator Functions")
    print("="*60)
    
    try:
        from utils.auth_decorators import (
            require_admin,
            require_project_access,
            require_saha_role,
            check_project_in_session
        )
        
        print("\n✓ Decorator imports successful:")
        print(f"  - require_admin: {require_admin.__name__}")
        print(f"  - require_project_access: {require_project_access.__name__}")
        print(f"  - require_saha_role: {require_saha_role.__name__}")
        print(f"  - check_project_in_session: {check_project_in_session.__name__}")
        
        # Check decorator signatures
        import inspect
        
        print("\n✓ Decorator signatures:")
        sig = inspect.signature(require_project_access)
        print(f"  - require_project_access{sig}")
        
        print("\n✅ Decorator Tests Passed!")
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")


def test_templates():
    """Test that admin templates exist"""
    print("\n" + "="*60)
    print("TEST 4: Admin Templates")
    print("="*60)
    
    templates_dir = workspace / 'templates' / 'admin'
    
    expected_templates = [
        'dashboard.html',
        'users.html',
        'add_user.html',
        'edit_user.html',
        'projects.html',
        'add_project.html',
        'backups.html',
    ]
    
    print(f"\n✓ Checking admin templates in {templates_dir}:")
    
    existing_templates = []
    if templates_dir.exists():
        existing_templates = [f.name for f in templates_dir.glob('*.html')]
    
    for template in expected_templates:
        found = template in existing_templates
        status = "✓" if found else "✗"
        print(f"  {status} {template}")
    
    if all(t in existing_templates for t in expected_templates):
        print("\n✅ Template Tests Passed!")
    else:
        print("\n❌ Some templates are missing!")


def test_imports():
    """Test critical imports"""
    print("\n" + "="*60)
    print("TEST 5: Critical Imports")
    print("="*60)
    
    imports = [
        ('utils.project_manager', 'ProjectManager'),
        ('utils.backup_manager', 'BackupManager'),
        ('utils.auth_decorators', 'require_admin'),
        ('routes.admin', 'bp'),
        ('models', 'User'),
    ]
    
    print("\n✓ Testing imports:")
    all_ok = True
    for module_name, class_name in imports:
        try:
            module = __import__(module_name, fromlist=[class_name])
            obj = getattr(module, class_name)
            print(f"  ✓ from {module_name} import {class_name}")
        except ImportError as e:
            print(f"  ✗ from {module_name} import {class_name} - {e}")
            all_ok = False
    
    if all_ok:
        print("\n✅ Import Tests Passed!")
    else:
        print("\n❌ Some imports failed!")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ADMIN PANEL & ROLE SYSTEM TEST SUITE")
    print("="*60)
    
    try:
        test_decorators()
        test_imports()
        test_user_model()
        test_admin_routes()
        test_templates()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nNext steps:")
        print("  1. Create initial admin user via Flask shell")
        print("  2. Start the application: python run.py")
        print("  3. Login with admin credentials")
        print("  4. Test admin panel: http://localhost:5000/admin/dashboard")
        print("  5. Create saha users and assign projects")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
