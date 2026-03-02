#!/usr/bin/env python
"""Quick test - Admin section visible?"""

import requests
import sys
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

try:
    s = requests_retry_session()
    
    # Step 1: Login
    print("[1] Logging in as admin...")
    resp = s.post('http://localhost:5000/login', 
        data={'username': 'admin', 'password': 'admin123'},
        allow_redirects=True,
        timeout=10
    )
    
    if resp.status_code != 200:
        print(f"    ✗ Login failed: {resp.status_code}")
        sys.exit(1)
    
    print(f"    ✓ Logged in (status: {resp.status_code})")
    
    # Step 2: Get dashboard
    print("\n[2] Getting dashboard...")
    resp = s.get('http://localhost:5000/dashboard/', timeout=10)
    
    if resp.status_code != 200:
        print(f"    ✗ Dashboard failed: {resp.status_code}")
        if resp.status_code == 302:
            print(f"    Redirect: {resp.headers.get('Location')}")
        sys.exit(1)
    
    html = resp.text
    
    # Check for admin section
    checks = {
        "Debug comment": "current_user.role" in html,
        "Role = admin": 'role = "admin"' in html,
        "Yönetim başlığı": "Yönetim" in html and "sidebar-menu-title" in html,
        "Yetki Yönetimi link": "Yetki Yönetimi" in html,
        "admin.yetkilendirme": "admin/yetkilendirme" in html or "/admin/yetkilendirme" in html,
    }
    
    print(f"\n[3] Checks:")
    all_pass = True
    for check, result in checks.items():
        status = "✓" if result else "✗"
        print(f"    {status} {check}: {result}")
        if not result:
            all_pass = False
    
    if all_pass:
        print("\n✅ ALL CHECKS PASSED - Sidebar should show 'Yetki Yönetimi'")
    else:
        print("\n❌ SOME CHECKS FAILED")
        # Show FULL admin section
        if "Yönetim" in html and "sidebar-menu-title" in html:
            # Find admin section
            import re
            match = re.search(r'{% if current_user\.role == .admin' , html)
            if match:
                idx = html.find('sidebar-menu-title">Yönetim</div>')
                if idx > 0:
                    snippet = html[idx:idx+2000]
                    print(f"\n=== ADMIN SECTION HTML ===\n{snippet}\n=== END ===")
            else:
                # Just find Yönetim section
                idx = html.find('Yönetim')
                snippet = html[max(0, idx-100):idx+1500]
                print(f"\n=== AREA AROUND 'Yönetim' ===\n{snippet}\n=== END ===")
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
