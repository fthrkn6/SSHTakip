#!/usr/bin/env python
"""Test if management_dashboard.html renders correctly"""

from app import create_app
from flask import render_template
import traceback as tb

app = create_app()

with app.test_request_context():
    print("=" * 60)
    print("Testing management_dashboard.html rendering")
    print("=" * 60)
    
    try:
        html = render_template('management_dashboard.html')
        print(f"[OK] Template rendered successfully ({len(html)} bytes)")
        
        # Check key elements
        checks = [
            ('id="projectsGrid"' in html, 'projectsGrid element'),
            ('id="projectCardTemplate"' in html, 'projectCardTemplate'),
            ('function loadProjects' in html, 'loadProjects function'),
            ('/reports/api/projects-kpi' in html, 'API URL'),
            ('<script>' in html, 'Script tags'),
            ('{% block content %}' not in html, 'Block tags removed (template rendered)'),
            ('management-container' in html, 'management-container'),
        ]
        
        print("\nElement checks:")
        all_good = True
        for check, name in checks:
            status = '[YES]' if check else '[NO]'
            print(f"  {status} {name}")
            if not check:
                all_good = False
        
        if not all_good:
            # Try to find where rendering stopped
            if 'management-container' in html:
                idx = html.find('management-container')
                print(f"\n[OK] Found management-container at position {idx}")
                print(f"Content after management-container: {html[idx+20:idx+200]}...")
                
    except Exception as e:
        print(f"[ERROR] ERROR rendering template: {e}")
        print("\nFull traceback:")
        tb.print_exc()

