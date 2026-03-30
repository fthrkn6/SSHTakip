#!/usr/bin/env python
"""Test if FRACAS chart data is being generated"""

import pandas as pd
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from routes.fracas import load_fracas_data, calculate_pareto_analysis, calculate_trend_analysis

print("\n" + "=" * 80)
print("TESTING FRACAS DATA GENERATION FOR CHARTS")
print("=" * 80)

# Create Flask app context
app = create_app()
with app.app_context():
    from flask import session
    session['current_project'] = 'belgrad'
    
    # Load data for belgrad
    df = load_fracas_data('belgrad')

app = create_app()
with app.app_context():
    from flask import session
    session['current_project'] = 'belgrad'
    
    # Load data for belgrad
    df = load_fracas_data('belgrad')
    
    if df is None:
        print("❌ Error: Could not load FRACAS data")
        sys.exit(1)
    
    print(f"\n✓ Loaded FRACAS data: {len(df)} rows")
    print(f"  Columns: {len(df.columns)}")
    
    # Test pareto analysis
    print("\n--- PARETO ANALYSIS ---")
    pareto = calculate_pareto_analysis(df)
    
    print(f"✓ by_module: {len(pareto['by_module'])} items")
    if pareto['by_module']:
        for item in pareto['by_module'][:3]:
            print(f"    - {item['name']}: {item['count']} ({item['percentage']}%)")
    else:
        print("    ❌ NO DATA!")
    
    print(f"✓ by_supplier: {len(pareto['by_supplier'])} items")
    if pareto['by_supplier']:
        for item in pareto['by_supplier'][:3]:
            print(f"    - {item['name']}: {item['count']} ({item['percentage']}%)")
    else:
        print("    ❌ NO DATA!")
    
    print(f"✓ by_location: {len(pareto['by_location'])} items")
    if pareto['by_location']:
        for item in pareto['by_location'][:3]:
            print(f"    - {item['name']}: {item['count']} ({item['percentage']}%)")
    else:
        print("    ❌ NO DATA!")
    
    print(f"✓ by_failure_class: {len(pareto['by_failure_class'])} items")
    if pareto['by_failure_class']:
        for item in pareto['by_failure_class']:
            print(f"    - {item['name']}: {item['count']} ({item['percentage']}%)")
    else:
        print("    ❌ NO DATA!")
    
    # Test trend analysis
    print("\n--- TREND ANALYSIS ---")
    trend = calculate_trend_analysis(df)
    
    print(f"✓ monthly: {len(trend['monthly'])} items")
    if trend['monthly']:
        for item in trend['monthly'][-3:]:
            print(f"    - {item['period']}: {item['count']}")
    else:
        print("    ❌ NO DATA!")
    
    print(f"✓ by_hour: {len(trend['by_hour'])} items")
    if trend['by_hour']:
        hourly_with_data = [h for h in trend['by_hour'] if h['count'] > 0]
        print(f"    Hours with data: {len(hourly_with_data)}/24")
    else:
        print("    ❌ NO DATA!")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
