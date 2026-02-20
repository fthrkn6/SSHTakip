#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug nearest maintenance calculation"""

import json
from app import create_app

app = create_app()
client = app.test_client()

response = client.get('/api/bakim-verileri')
data = json.loads(response.data)

# Check tram 1531 (36000 KM)
tram = [t for t in data['tramps'] if t['tram_id'] == '1531'][0]

print("TRAM 1531 - Current KM: 30000")
print("="*80)

nearest = tram['nearest_maintenance']
all_maint = tram['all_maintenances']

print("\nAll maintenances sorted by km_left:")
maint_list = [(level, m['km_left'], m['next_km'], m['status']) for level, m in all_maint.items()]
maint_list.sort(key=lambda x: (x[1] if x[1] > 0 else float('inf')))  # Sort by km_left, put 0s at end

for level, km_left, next_km, status in maint_list:
    marker = " ← NEAREST" if level == nearest['level'] else ""
    print(f"  {level:5s}: Next {next_km:7d} KM | Left {km_left:6d} KM | {status:10s}{marker}")

print(f"\nSelected Nearest: {nearest['level']} | Status: {nearest['status']} | KM Left: {nearest['km_left']}")

# The issue is that multiple levels have the same next_km (36000)
# when current KM is 30000:
# - 6K: next=36000 (6*6000), km_left=6000
# - 18K: next=36000 (2*18000), km_left=6000  
# - 36K: next=36000 (1*36000), km_left=6000
# So we need to pick the first one found with the smallest km_left
