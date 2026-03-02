#!/usr/bin/env python
import requests

session = requests.Session()

# Login
login_resp = session.post('http://localhost:5000/login', data={
    'username': 'admin',
    'password': 'admin123'
})

if login_resp.status_code != 200:
    print(f"Login failed: {login_resp.status_code}")
    exit(1)

# Get /admin/users
resp = session.get('http://localhost:5000/admin/users')
html = resp.text

# Find the admin section
admin_start = html.find('Yönetim</div>')
if admin_start == -1:
    print("Admin section not found")
    exit(1)

# Extract 4000 chars starting from admin title
section = html[admin_start:admin_start+4000]

# Find where audit log link ends
audit_end = section.find('Denetim Günlüğü</span>')
if audit_end == -1:
    print("Audit log not found")
    exit(1)

audit_end = section.find('</a>', audit_end) + 4  # include </a>

# Show what comes AFTER audit log
print("Content AFTER audit log link:")
print("=" * 60)
after_audit = section[audit_end:audit_end+1000]
print(repr(after_audit))
print("\n" + "=" * 60)
print("Formatted:")
print(after_audit)
