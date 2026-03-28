#!/usr/bin/env python
"""Quick test for dashboard-yonetim page and projects-kpi API"""

import requests
import json
from time import sleep

BASE_URL = 'http://localhost:5000'

def test_api():
    """Test the API endpoint directly"""
    print("\n=== Testing /reports/api/projects-kpi ===")
    url = f'{BASE_URL}/reports/api/projects-kpi'
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ API Success!")
            print(f"Response keys: {list(data.keys())}")
            if 'data' in data:
                projects = list(data['data'].keys())
                print(f"Projects returned: {projects}")
                print(f"Total projects: {len(projects)}")
                for proj, info in data['data'].items():
                    print(f"  - {proj}: {info.get('name', 'N/A')} ({info.get('vehicles', '?')} vehicles)")
        else:
            print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_dashboard_page():
    """Test the dashboard page loading"""
    print("\n=== Testing /reports/dashboard-yonetim page ===")
    url = f'{BASE_URL}/reports/dashboard-yonetim'
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Length: {response.headers.get('Content-Length')}")
        
        if response.status_code == 200:
            html = response.text
            print(f"✅ Page loaded successfully ({len(html)} bytes)")
            
            # Check for key elements
            checks = [
                ('projectsGrid' in html, 'projectsGrid element'),
                ('projectCardTemplate' in html, 'projectCardTemplate'),
                ('loadProjects' in html, 'loadProjects function'),
                ("'/reports/api/projects-kpi'" in html, 'API fetch URL'),
                ('<script>' in html, 'Script tags'),
            ]
            
            for check, name in checks:
                status = '✅' if check else '❌'
                print(f"{status} {name}")
            
            # Show first 1000 chars to see structure
            print(f"\nFirst 1000 chars of HTML:")
            print(html[:1000])
            print("\n... (truncated)")
            
            # Search for specific keywords
            print(f"\nSearching for keywords:")
            keywords = ['management-container', 'DOCTYPE', 'html', 'body', 'script']
            for kw in keywords:
                count = html.count(kw)
                print(f"  '{kw}': {count} occurrences")
        else:
            print(f"❌ Status {response.status_code}: {response.text[:500]}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    print("Dashboard Testing Script")
    print("=" * 50)
    
    test_api()
    sleep(1)
    test_dashboard_page()
