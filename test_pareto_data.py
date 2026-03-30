#!/usr/bin/env python
"""Check if pareto data is properly prepared"""
from flask import Flask, session
from routes.fracas import load_fracas_data, calculate_pareto_analysis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'

with app.app_context():
    with app.test_request_context():
        session['current_project'] = 'belgrad'
        df = load_fracas_data()
        pareto = calculate_pareto_analysis(df)
        
        print(f"by_module items: {len(pareto['by_module'])}")
        if pareto['by_module']:
            print(f"First item: {pareto['by_module'][0]}")
            
            # Try list comprehension 
            try:
                labels = [item['name'][:20] for item in pareto['by_module']]
                print(f"✓ Labels created: {labels}")
            except Exception as e:
                print(f"✗ Error creating labels: {e}")
                print(f"Item keys: {pareto['by_module'][0].keys()}")
