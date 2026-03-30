#!/usr/bin/env python
"""Teste se os dados podem ser serializados para JSON"""
import json
import pandas as pd
from flask import json as flask_json, session
from routes.fracas import (
    load_fracas_data,
    calculate_basic_stats,
    calculate_rams_metrics,
    calculate_pareto_analysis,
    calculate_trend_analysis,
    calculate_supplier_analysis,
    calculate_cost_analysis
)

# Simular a sessão
from flask import Flask
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'test'

with app.app_context():
    with app.test_request_context():
        session['current_project'] = 'belgrad'
        df = load_fracas_data()
        
        if df is None:
            print("ERROR: Veri yüklenmedi!")
            exit(1)
        
        print(f"✓ Veri yüklendi: {len(df)} satır")
        
        try:
            stats = calculate_basic_stats(df)
            json.dumps(stats)
            print(f"✓ basic_stats serializável")
        except Exception as e:
            print(f"✗ basic_stats ERROR: {e}")
            print(stats)
        
        try:
            rams = calculate_rams_metrics(df)
            json.dumps(rams)
            print(f"✓ rams_metrics serializável")
        except Exception as e:
            print(f"✗ rams_metrics ERROR: {e}")
            print(rams)
        
        try:
            pareto = calculate_pareto_analysis(df)
            json.dumps(pareto)
            print(f"✓ pareto_analysis serializável")
        except Exception as e:
            print(f"✗ pareto_analysis ERROR: {e}")
            if pareto['by_module']:
                print("by_module sample:", pareto['by_module'][0])
        
        try:
            trend = calculate_trend_analysis(df)
            json.dumps(trend)
            print(f"✓ trend_analysis serializável")
        except Exception as e:
            print(f"✗ trend_analysis ERROR: {e}")
            if trend['monthly']:
                print("monthly sample:", trend['monthly'][0])
        
        try:
            supplier = calculate_supplier_analysis(df)
            json.dumps(supplier)
            print(f"✓ supplier_analysis serializável")
        except Exception as e:
            print(f"✗ supplier_analysis ERROR: {e}")
            if supplier['performance']:
                print("performance sample:", supplier['performance'][0])
        
        try:
            cost = calculate_cost_analysis(df)
            json.dumps(cost)
            print(f"✓ cost_analysis serializável")
        except Exception as e:
            print(f"✗ cost_analysis ERROR: {e}")
            print(cost)
        
        print("\n✓ Todos os dados podem ser serializados!")
