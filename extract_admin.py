#!/usr/bin/env python
"""Save full admin section to file"""

import requests

s = requests.Session()
s.post('http://localhost:5000/login', 
    data={'username': 'admin', 'password': 'admin123'},
    allow_redirects=True
)

resp = s.get('http://localhost:5000/dashboard/')
html = resp.text

# Find admin section
if 'sidebar-menu-title">Yönetim</div>' in html:
    idx = html.find('sidebar-menu-title">Yönetim</div>')
    # Extract admin section (find until next main divider or endif)
    end_idx = html.find('{% endif %}', idx)
    if end_idx < 0:
        end_idx = idx + 3000
    
    admin_section = html[idx:end_idx]
    
    # Save to file
    with open('admin_section.html', 'w', encoding='utf-8') as f:
        f.write(admin_section)
    
    print("Saved to admin_section.html")
    print(f"\nLength: {len(admin_section)} chars")
    print(f"'Yetki Yönetimi' in section: {'Yetki Yönetimi' in admin_section}")
    print(f"'/admin/yetkilendirme' in section: {'/admin/yetkilendirme' in admin_section}")
    
    # Show part containing links
    lines = admin_section.split('\n')
    print(f"\nTotal lines: {len(lines)}")
    print("\nLinks in section:")
    for i, line in enumerate(lines):
        if '<a href="' in line:
            # Get next 2 lines too
            link_part = '\n'.join(lines[i:min(i+3, len(lines))])
            print(f"  {link_part}")
