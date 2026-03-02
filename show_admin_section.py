#!/usr/bin/env python
"""Get full admin section HTML"""

import requests

s = requests.Session()

# Login
resp = s.post('http://localhost:5000/login', 
    data={'username': 'admin', 'password': 'admin123'},
    allow_redirects=True
)

# Get dashboard
resp = s.get('http://localhost:5000/dashboard/')
html = resp.text

# Find admin section and print ENTIRE section until {% endif %}
if 'sidebar-menu-title">Yönetim</div>' in html:
    idx = html.find('<div class="sidebar-menu-title">Yönetim</div>')
    end_idx = html.find('{% endif %}', idx)
    
    admin_section = html[idx:end_idx+20]
    
    print("=== FULL ADMIN SECTION ===")
    print(admin_section)
    print("=== END ===")
    
    # Check what's in it
    print("\n[SEARCH RESULTS]")
    print(f"'Yetki Yönetimi' in section: {'Yetki Yönetimi' in admin_section}")
    print(f"'admin.yetkilendirme' in section: {'admin.yetkilendirme' in admin_section}")
    print(f"'lock-fill' (Yetki icon) in section: {'lock-fill' in admin_section}")
