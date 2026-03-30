#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FRACAS index route'unu direkt test etmek
"""
from app import create_app
from flask import session as flask_session

app = create_app()

with app.app_context():
    with app.test_request_context('/fracas/', method='GET'):
        # Mock current_user
        from unittest.mock import Mock, patch
        from flask_login import current_user
        
        mock_user = Mock()
        mock_user.is_active = True
        mock_user.is_authenticated = True
        mock_user.get_id = lambda: 'testuser'
        
        flask_session['current_user'] = 'test'
        flask_session['current_project'] = 'belgrad'
        
        print("="* 60)
        print("DIRECT ROUTE TEST")
        print("=" * 60)
        print(f"\nSession current_project: {flask_session.get('current_project')}")
        
        # Import after app context
        from routes.fracas import index
        
        print("\nCalling index() route...")
        try:
            # Patch both login_required and current_user
            with patch('flask_login.utils._get_request') as mock_get_request, \
                 patch.object(current_user, 'is_authenticated', True):
                
                with patch('routes.fracas.current_user', mock_user):
                    response_html = index()
                    print(f"Response type: {type(response_html)}")
                
                if isinstance(response_html, str):
                    print(f"Response length: {len(response_html)} chars")
                    
                    checks = [
                        ('paretoModuleChart', 'Chart paretoModuleChart'),
                        ('new Chart', 'Chart.js init'),
                        ('Veri Yok', 'No data message'),
                    ]
                    
                    print("\nContent checks:")
                    for search_str, label in checks:
                        exists = search_str in response_html
                        symbol = '[OK]' if exists else '[FAIL]'
                        print(f"   {symbol} {label}")
                else:
                    print(f"Response object: {response_html}")
                    
        except Exception as e:
            import traceback
            print(f"ERROR: {e}")
            traceback.print_exc()

print("\n" + "=" * 60)
