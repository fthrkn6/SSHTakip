#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check template output for isletme kaynaklı"""

from app import create_app
from flask_login import LoginManager, UserMixin

app = create_app()

class MockUser(UserMixin):
    def __init__(self):
        self.id = 1
        self.username = 'test'
        self.role = 'admin'
    
    def get_role_display(self):
        return 'Yonetici'

login_manager = app.login_manager
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return MockUser()

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['_user_id'] = '1'
    
    response = client.get('/dashboard/')
    content = response.get_data(as_text=True)
    
    print("\n" + "="*70)
    print("TEMPLATE ICINDE 'ISLETME/WARNING' ARAYISI")
    print("="*70)
    
    # Find badge sections
    import re
    badges = re.findall(r'<span class="badge[^"]*>([^<]+)</span>', content)
    
    print(f"\nBulunun badge'ler ({len(badges)} toplam):")
    for i, badge in enumerate(badges[:20]):
        print(f"  {i}: '{badge}'")
    
    # Check for warning badge
    if 'bg-warning' in content:
        # Find context
        idx = content.find('bg-warning')
        snippet = content[max(0, idx-200):idx+200]
        print(f"\nWarning badge bulundu:")
        print(f"  Context: ...{snippet}...")
    
    # Check for İşletme text
    if 'İ' in content and 'şletme' in content:
        print(f"\nİsletme keywords bulundu")
    elif 'Isletme' in content:
        print(f"\nIsletme (ASCII) bulundu")
    else:
        print(f"\nNe İşletme ne Isletme bulunmadı")
    
    print("\n" + "="*70 + "\n")
