import requests

s = requests.Session()
s.post('http://localhost:5000/login', data={'username': 'admin', 'password': 'admin123'})
r = s.get('http://localhost:5000/admin/users')

# Extract admin section
idx = r.text.find('Yönetim</div>')
end_idx = r.text.find('</nav>', idx)
admin_section = r.text[idx:end_idx+6]

print("=== ADMIN SECTION (CLEAN OUTPUT) ===\n")
print(admin_section)
print("\n=== END ADMIN SECTION ===")

# List all links found
links = []
import re
for match in re.finditer(r'href="([^"]+)"[^>]*>\s*([^<]*(?:<[^>]*>[^<]*)*)\s*</a>', admin_section):
    href = match.group(1)
    if 'admin' in href or 'audit' in href or 'kullanicilar' in href:
        links.append(href)

print(f"\n=== LINKS IN ADMIN SECTION ({len(links)}/7 expected) ===")
for i, link in enumerate(links, 1):
    print(f"{i}. {link}")
