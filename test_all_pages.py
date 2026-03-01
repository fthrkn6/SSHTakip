#!/usr/bin/env python
"""
Test script to verify KPI, FRACAS, and Authorization pages are working
"""
from app import create_app
from models import db, User, Role
import sys

app = create_app()

def test_pages():
    """Test all three pages"""
    
    # Setup: Create admin user for testing
    with app.app_context():
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', email='admin@test.com', full_name='Admin', role='admin')
            admin_user.set_password('admin')
            db.session.add(admin_user)
            db.session.commit()
    
    tests = {
        '/kpi/': 'KPI Dashboard',
        '/fracas/': 'FRACAS Analiz',
        '/admin/yetkilendirme': 'Yetkilendirme Yönetimi',
    }
    
    results = []
    
    with app.test_client() as client:
        # Login as admin
        login_resp = client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
        if login_resp.status_code != 200:
            print("❌ Admin login failed")
            return False
        
        print("✓ Admin user logged in\n")
        
        # Test each page
        for url, page_name in tests.items():
            print(f"Testing {page_name} ({url})...")
            resp = client.get(url, follow_redirects=True)
            
            is_success = resp.status_code == 200
            status_text = f"✓ Status {resp.status_code}" if is_success else f"✗ Status {resp.status_code}"
            
            results.append({
                'page': page_name,
                'url': url,
                'status': resp.status_code,
                'success': is_success
            })
            
            # Check for content
            html = resp.get_data(as_text=True)
            content_checks = []
            
            if page_name == 'KPI Dashboard':
                if 'KPI' in html and 'EN 15341' in html:
                    content_checks.append('✓ KPI content found')
                if 'permission-toggle' in html or '500' not in resp.get_data(as_text=True):
                    content_checks.append('✓ No 500 error detected')
                    
            elif page_name == 'FRACAS Analiz':
                if 'FRACAS' in html or 'Arıza' in html:
                    content_checks.append('✓ FRACAS content found')
                if 'permission-toggle' in html or '500' not in resp.get_data(as_text=True):
                    content_checks.append('✓ No 500 error detected')
                    
            elif page_name == 'Yetkilendirme Yönetimi':
                if 'Yetkilendirme Yönetimi' in html:
                    content_checks.append('✓ Authorization page title found')
                if 'Yeni Rol Ekle' in html:
                    content_checks.append('✓ Add Role button found')
                if 'addRoleModal' in html:
                    content_checks.append('✓ Add Role modal found')
                if 'deleteRoleModal' in html:
                    content_checks.append('✓ Delete Role modal found')
                if 'permission-toggle' in html:
                    content_checks.append('✓ Permission matrix found')
            
            print(f"  {status_text}")
            for check in content_checks:
                print(f"  {check}")
            print()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    all_passed = all(r['success'] for r in results)
    
    for result in results:
        symbol = "✓" if result['success'] else "✗"
        print(f"{symbol} {result['page']}: {result['status']}")
    
    print("="*50)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        return True
    else:
        print("✗ SOME TESTS FAILED")
        return False

if __name__ == '__main__':
    try:
        success = test_pages()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
