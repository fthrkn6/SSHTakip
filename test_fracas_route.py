"""
Test the /fracas/ route to see what data is being returned
"""
import sys
sys.path.insert(0, 'c:\\Users\\fatiherkin\\Desktop\\bozankaya_ssh_takip')

from app import create_app
from flask import session
import json

app = create_app()

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['current_project'] = 'timisoara'
    
    response = client.get('/fracas/')
    
    # Check response status
    print(f"Response status: {response.status_code}")
    print(f"Response type: {type(response)}")
    
    # Try to extract the data from response
    html = response.get_data(as_text=True)
    
    # Look for the pareto data in the template
    if "paretoModuleChart" in html:
        print("\n✓ Chart canvas found in HTML")
        
        # Look for the data arrays
        if "'MC'" in html or '"MC"' in html:
            print("✓ Module data found in HTML")
        else:
            print("✗ Module data NOT found in HTML")
            
        if "labels:" in html and "data:" in html:
            print("✓ Chart configuration found in HTML")
        else:
            print("✗ Chart configuration NOT found in HTML")
    else:
        print("\n✗ Chart canvas NOT found in HTML")
    
    # Check for specific data indicators
    if "by_module" in html:
        print("✓ by_module key found in HTML")
    else:
        print("✗ by_module key NOT found in HTML")
    
    # Look for any empty pareto checks
    if "{% if pareto.by_module %}" in html:
        print("∓ Template conditional still in HTML (not processed)")
    
    # Print first 5000 chars of relevant section
    chart_start = html.find("paretoModuleChart")
    if chart_start > 0:
        print(f"\nChart section (chars {chart_start} to {chart_start+1000}):")
        print(html[chart_start-200:chart_start+1000])
