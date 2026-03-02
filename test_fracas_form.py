#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test FRACAS ID in form for GET request"""

from app import app
import re

with app.test_client() as client:
    # Set session
    with client.session_transaction() as sess:
        sess['current_project'] = 'belgrad'
    
    # GET request to ariza_bildir
    response = client.get('/ariza_bildir', follow_redirects=False)
    
    print(f'Response Status: {response.status_code}')
    if response.status_code == 200:
        html = response.get_data(as_text=True)
        
        # Search for FRACAS ID in form value or text
        # Pattern 1: value="BOZ-BEL25-FF-XXX"
        match = re.search(r'value=["\']?(BOZ-BEL25-FF-\d{3})["\']?', html)
        if match:
            print(f'✓ FRACAS ID in form value: {match.group(1)}')
        else:
            # Pattern 2: placeholder with next ID
            match = re.search(r'placeholder=["\']?(BOZ-BEL25-FF-\d{3})["\']?', html)
            if match:
                print(f'✓ FRACAS ID as placeholder: {match.group(1)}')
            else:
                # Pattern 3: Look in text content
                if 'BOZ-BEL25-FF-' in html:
                    ids = re.findall(r'BOZ-BEL25-FF-(\d{3})', html)
                    print(f'Found FRACAS IDs in page: {ids}')
                    if ids:
                        print(f'✓ Next ID should be around: BOZ-BEL25-FF-{max(int(i) for i in ids) + 1:03d}')
                else:
                    print('❌ No FRACAS ID found in form')
                    
                    # Debug
                    fracas_idx = html.find('fracas_id')
                    if fracas_idx > 0:
                        print(f'\nDebug - Found fracas_id at position {fracas_idx}')
                        print(f'Context: {html[max(0, fracas_idx-200):fracas_idx+300]}')
    else:
        print(f'❌ Request failed with status {response.status_code}')
