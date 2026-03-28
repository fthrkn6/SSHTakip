import requests

response = requests.get('http://localhost:5000/reports/dashboard-yonetim')
with open('dashboard_response.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

text = response.text
print(f'Saved {len(text)} bytes to dashboard_response.html')
print(f'Contains projectsGrid: {"projectsGrid" in text}')
print(f'Contains projectCardTemplate: {"projectCardTemplate" in text}')
print(f'Contains loadProjects: {"loadProjects" in text}')
print(f'\nFirst 500 chars:\n{text[:500]}')
print(f'\nLast 500 chars:\n{text[-500:]}')

# Search for specific strings
block_content = text.find('block content')
if block_content > 0:
    print(f'\nFound "block content" at position {block_content}')
else:
    print('\nNOT FOUND: "block content" - template may not be rendered!')
