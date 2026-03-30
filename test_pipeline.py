#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import create_app
from flask import session as flask_session

app = create_app()

with app.app_context():
    with app.test_request_context('/'):
        from routes.fracas import (
            load_fracas_data,
            calculate_basic_stats,
            calculate_pareto_analysis,
            calculate_basic_stats
        )
        
        print("TEST: FRACAS calculation pipeline\n")
        
        for project_code in ['belgrad', 'timisoara']:
            print(f"\n{project_code.upper()}:")
            df = load_fracas_data(project_code)
            
            if df is None:
                print(f"  1. load_fracas_data(): FAIL")
                continue
                
            print(f"  1. load_fracas_data(): OK ({len(df)} rows)")
            
            stats = calculate_basic_stats(df)
            print(f"  2. calculate_basic_stats(): OK ({stats.get('total_failures', '?')} failures)")
            
            pareto = calculate_pareto_analysis(df)
            module_count = len(pareto.get('by_module', []))
            supplier_count = len(pareto.get('by_supplier', []))
            print(f"  3. calculate_pareto_analysis(): OK (module={module_count}, supplier={supplier_count})")
