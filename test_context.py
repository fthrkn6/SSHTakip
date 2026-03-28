#!/usr/bin/env python
"""Flask app context'inde template render'ını test et"""

from app import create_app
from flask import render_template

app = create_app()

with app.test_request_context():
    try:
        print("[TEST] Rendering management_dashboard.html in request context...")
        
        html = render_template('management_dashboard.html')
        
        print(f"[SUCCESS] Rendered {len(html)} bytes")
        print(f"[Check] Has projectsGrid: {'id=\"projectsGrid\"' in html}")
        print(f"[Check] Has loadProjects: {'function loadProjects' in html}")
        
        # Show where it ends
        if 'management-container' in html:
            idx = html.rfind('management-container')
            print(f"[DEBUG] Last 'management-container' at position {idx}")
            print(f"[DEBUG] Content ends with: ...{html[-100:]}")
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
