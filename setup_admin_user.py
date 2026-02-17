#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Initialize Admin User - Setup Script
Create the first admin user for the system
"""

import os
import sys
from pathlib import Path

# Add workspace to path
workspace = Path(__file__).parent
sys.path.insert(0, str(workspace))

def create_admin_user():
    """Create initial admin user"""
    from app import create_app
    from models import db, User
    
    app = create_app()
    
    with app.app_context():
        # Check if admin user already exists
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print(f"⚠️  Admin user 'admin' already exists!")
            return False
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@bozankaya.com',
            full_name='Sistem Yöneticisi',
            role='admin'
        )
        admin.set_password('Admin123!')
        admin.set_assigned_projects(['*'])
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Admin User Created Successfully!")
        print("="*50)
        print(f"  Username: admin")
        print(f"  Password: Admin123!")
        print(f"  Email: admin@bozankaya.com")
        print(f"  Full Name: Sistem Yöneticisi")
        print(f"  Role: Admin (Yönetici)")
        print(f"  Projects: All (*)")
        print("="*50)
        print("\n⚠️  IMPORTANT: Change password after first login!")
        print("    URL: http://localhost:5000/profile")
        
        return True


def create_demo_saha_users():
    """Create demo saha users for testing"""
    from app import create_app
    from models import db, User
    
    app = create_app()
    
    with app.app_context():
        demo_users = [
            {
                'username': 'saha_belgrad',
                'email': 'belgrad@bozankaya.com',
                'full_name': 'Belgrad Saha Teknikeri',
                'projects': ['belgrad']
            },
            {
                'username': 'saha_multi',
                'email': 'multi@bozankaya.com',
                'full_name': 'Multi-Proje Teknisyeni',
                'projects': ['belgrad', 'gebze', 'ankara']
            },
        ]
        
        created_count = 0
        for user_data in demo_users:
            # Check if user already exists
            existing = User.query.filter_by(username=user_data['username']).first()
            if existing:
                print(f"⚠️  User '{user_data['username']}' already exists, skipping...")
                continue
            
            # Create user
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                role='saha'
            )
            user.set_password('Saha123!')
            user.set_assigned_projects(user_data['projects'])
            
            db.session.add(user)
            created_count += 1
        
        if created_count > 0:
            db.session.commit()
            print(f"\n✅ Created {created_count} Demo Saha Users!")
            print("="*50)
            for user_data in demo_users:
                if not User.query.filter_by(username=user_data['username']).first().created_at is None:
                    print(f"  Username: {user_data['username']}")
                    print(f"    Password: Saha123!")
                    print(f"    Projects: {', '.join(user_data['projects'])}")
            print("="*50)
        else:
            print("⚠️  All demo users already exist.")


def list_users():
    """List all users in the system"""
    from app import create_app
    from models import db, User
    
    app = create_app()
    
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("❌ No users found in the system.")
            return
        
        print("\n" + "="*80)
        print("SYSTEM USERS")
        print("="*80)
        print(f"{'Username':<20} {'Full Name':<25} {'Role':<10} {'Projects':<20}")
        print("-"*80)
        
        for user in users:
            role = "Admin" if user.is_admin() else "Saha"
            projects = user.get_assigned_projects()
            if projects == '*':
                projects_str = "All"
            else:
                projects_str = ", ".join(projects[:2])
                if len(projects) > 2:
                    projects_str += f" +{len(projects)-2}"
            
            print(f"{user.username:<20} {user.full_name:<25} {role:<10} {projects_str:<20}")
        
        print("="*80)


def main():
    """Main setup flow"""
    print("\n" + "="*60)
    print("ADMIN USER SETUP - BOOT STRAP SCRIPT")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("  1. Create initial admin user")
        print("  2. Create demo saha users for testing")
        print("  3. List all users in system")
        print("  4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            print("\n" + "-"*60)
            success = create_admin_user()
            if not success:
                print("❌ Failed to create admin user")
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            print("\n" + "-"*60)
            create_demo_saha_users()
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            print()
            list_users()
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please try again.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
