#!/usr/bin/env python
"""Direct template render test - no Flask server"""

from jinja2 import Environment, FileSystemLoader
import os

# Change to templates directory
os.chdir('templates')

env = Environment(loader=FileSystemLoader('.'))

try:
    # Get the raw content of management_dashboard.html
    with open('management_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"[FILE SIZE] management_dashboard.html: {len(content)} bytes")
    print(f"[HAS projectsGrid] {'id=\"projectsGrid\"' in content}")
    print(f"[HAS loadProjects] {'function loadProjects' in content}")
    print(f"[HAS projectCardTemplate] {'id=\"projectCardTemplate\"' in content}")
    
    # Check for url_for issues in file
    if 'reports.management_report' in content:
        print(f"[ERROR] File still has 'reports.management_report'")
    if 'reports.management_dashboard' in content:
        print(f"[OK] File has 'reports.management_dashboard'")
        
except Exception as e:
    print(f"ERROR: {e}")
