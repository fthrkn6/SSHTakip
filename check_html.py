#!/usr/bin/env python
"""Quick form check using requests"""
import requests
import json
import re

url = "http://localhost:5000/servis_durumu"
try:
    print("Fetching page...")
    response = requests.get(url)
    
    # Check sistem select in HTML
    print("\n✓ Checking HTML...")
    if 'sistemSelect' in response.text:
        print("  ✓ sistemSelect found in HTML")
        
        # Find the sistem select line
        for line in response.text.split('\n'):
            if 'sistemSelect' in line and 'select' in line:
                print(f"  Found: {line.strip()[:100]}...")
                break
    
    # Check JavaScript functions
    print("\n✓ Checking JavaScript...")
    checks = [
        ('updateFormFields', 'updateFormFields function'),
        ('setFieldDisabled', 'setFieldDisabled function'),
        ('const sistemler_data', 'sistemler_data variable'),
        ('statusSelect.addEventListener', 'statusSelect event listener'),
        ('sistemSelect.addEventListener', 'sistemSelect event listener'),
    ]
    
    for pattern, label in checks:
        if pattern in response.text:
            print(f"  ✓ {label}")
        else:
            print(f"  ✗ {label}")
    
    # Extract sistemler_data
    print("\n✓ Extracting sistemler_data...")
    match = re.search(r'const sistemler_data = (\{.*?\});', response.text, re.DOTALL)
    if match:
        try:
            data_str = match.group(1)
            # Count systems
            systems = re.findall(r'"([^"]+)":\s*\{', data_str)
            print(f"  Systems found: {len(systems)}")
            for sys in systems:
                print(f"    - {sys}")
        except:
            print("  Could not parse sistemler_data")
    
    print("\n✓ All checks passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
