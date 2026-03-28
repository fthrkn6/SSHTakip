import requests

s = requests.Session()
# Login
login_resp = s.post('http://localhost:5000/login', data={'username': 'admin', 'password': 'admin'}, allow_redirects=False)
print(f'Login status: {login_resp.status_code}')

# Now access dashboard
resp = s.get('http://localhost:5000/reports/dashboard-yonetim')
print(f'Dashboard status: {resp.status_code}')
print(f'Content size: {len(resp.text)}')

checks = {
    'projectsGrid': 'projectsGrid' in resp.text,
    'loadProjects': 'loadProjects' in resp.text,
    'management-container': 'management-container' in resp.text,
    'projectCardTemplate': 'projectCardTemplate' in resp.text,
    'projects-kpi': 'projects-kpi' in resp.text,
}
for k, v in checks.items():
    print(f'  {k}: {v}')

# Test API
api_resp = s.get('http://localhost:5000/reports/api/projects-kpi')
print(f'\nAPI status: {api_resp.status_code}')
if api_resp.status_code == 200:
    data = api_resp.json()
    print(f'API success: {data.get("success")}')
    if data.get('data'):
        print(f'Projects: {list(data["data"].keys())}')

# Test /api/projects
proj_resp = s.get('http://localhost:5000/api/projects')
print(f'\n/api/projects status: {proj_resp.status_code}')
if proj_resp.status_code == 200:
    projects = proj_resp.json()
    print(f'Projects count: {len(projects)}')
    if projects:
        print(f'First: {projects[0]}')
