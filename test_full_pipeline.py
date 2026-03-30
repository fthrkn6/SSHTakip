#!/usr/bin/env python
"""Test the full FRACAS analysis pipeline"""
import sys
sys.path.insert(0, 'c:\\Users\\fatiherkin\\Desktop\\bozankaya_ssh_takip')

from app import create_app
from flask import session
from routes.fracas import load_fracas_data, calculate_basic_stats, calculate_pareto_analysis, calculate_trend_analysis

app = create_app()

with app.test_request_context():
    # Set session
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['current_project'] = 'timisoara'
    
    # Try loading data
    print("Loading FRACAS data for timisoara...")
    df = load_fracas_data('timisoara')
    
    if df is not None:
        print(f"✓ Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Try calculations
        try:
            print("\nCalculating basic stats...")
            stats = calculate_basic_stats(df)
            print(f"✓ Stats complete: {stats}")
            
            print("\nCalculating pareto...")
            pareto = calculate_pareto_analysis(df)
            print(f"✓ Pareto complete: {len(pareto['by_module'])} modules, {len(pareto['by_supplier'])} suppliers")
            
            print("\nCalculating trend...")
            trend = calculate_trend_analysis(df)
            print(f"✓ Trend complete: {len(trend['monthly'])} months")
            
        except Exception as e:
            print(f"✗ Calculation error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("✗ No data loaded")
