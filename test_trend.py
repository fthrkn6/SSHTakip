#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import app
import json

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['current_project'] = 'belgrad'
    
    # Make request after session is set
    with client.session_transaction() as sess:
        pass  # Keep session alive
    
    resp = client.get('/reports/scenarios/availability-trend?period=gunluk')
    print('=' * 60)
    print(f'Status: {resp.status_code}')
    
    if resp.status_code == 200:
        try:
            data = resp.get_json()
            print(f'Success: {data.get("success")}')
            
            if data.get('success'):
                print(f'Period: {data.get("period")}')
                print(f'Granularity: {data.get("granularity")}')
                
                trend_data = data.get('data', {})
                dates = trend_data.get('dates', [])
                avgs = trend_data.get('averages', [])
                
                print(f'Dates count: {len(dates)}')
                print(f'Averages count: {len(avgs)}')
                
                if dates:
                    print(f'Date range: {dates[0]} to {dates[-1]}')
                if avgs:
                    print(f'Sample averages: {avgs[:7]}')
                    print(f'Min: {min(avgs):.1f}%, Max: {max(avgs):.1f}%, Avg: {sum(avgs)/len(avgs):.1f}%')
            else:
                print(f'Error: {data.get("error")}')
        except Exception as e:
            print(f'JSON Error: {e}')
            print(f'Content: {resp.data[:500]}')
    else:
        print('Response:')
        print(resp.data.decode('utf-8')[:500])

print('=' * 60)
