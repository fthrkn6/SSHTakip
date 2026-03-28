#!/usr/bin/env python
"""Check if CSP header is being set correctly"""

import urllib.request

try:
    resp = urllib.request.urlopen('http://localhost:5000/login')
    headers = dict(resp.headers)
    
    print('=== Response Headers ===')
    for key in sorted(headers.keys()):
        if 'content' in key.lower() or 'security' in key.lower() or 'cache' in key.lower():
            value = headers[key]
            if len(value) > 80:
                print(f'{key}: {value[:80]}...')
            else:
                print(f'{key}: {value}')
    
    if 'Content-Security-Policy' in headers:
        print('\n✅ CSP Header Found!')
        print(f'\nFull CSP Policy:\n{headers["Content-Security-Policy"]}')
    else:
        print('\n❌ CSP Header NOT Found in response')
        
except Exception as e:
    print(f'Error: {e}')
