#!/usr/bin/env python
"""Timişoara verisini test et"""
import json
from flask import Flask, session
from routes.fracas import (
    load_fracas_data,
    calculate_basic_stats,
    calculate_rams_metrics,
    calculate_pareto_analysis,
    calculate_trend_analysis,
    calculate_supplier_analysis,
    calculate_cost_analysis
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'

with app.app_context():
    # Timişoara testi
    with app.test_request_context():
        session['current_project'] = 'timisoara'
        df = load_fracas_data()
        
        if df is None:
            print("❌ Timişoara: Veri yüklenmedi!")
        else:
            print(f"✓ Timişoara yüklendi: {len(df)} satır")
            
            try:
                stats = calculate_basic_stats(df)
                json.dumps(stats)
                print(f"✓ basic_stats OK")
            except Exception as e:
                print(f"❌ basic_stats: {e}")
            
            try:
                rams = calculate_rams_metrics(df)
                json.dumps(rams)
                print(f"✓ rams_metrics OK")
            except Exception as e:
                print(f"❌ rams_metrics: {e}")
            
            try:
                pareto = calculate_pareto_analysis(df)
                json.dumps(pareto)
                print(f"✓ pareto_analysis OK")
            except Exception as e:
                print(f"❌ pareto_analysis: {e}")
            
            try:
                trend = calculate_trend_analysis(df)
                json.dumps(trend)
                print(f"✓ trend_analysis OK")
            except Exception as e:
                print(f"❌ trend_analysis: {e}")
                import traceback
                traceback.print_exc()
            
            try:
                supplier = calculate_supplier_analysis(df)
                json.dumps(supplier)
                print(f"✓ supplier_analysis OK")
            except Exception as e:
                print(f"❌ supplier_analysis: {e}")
            
            try:
                cost = calculate_cost_analysis(df)
                json.dumps(cost)
                print(f"✓ cost_analysis OK")
            except Exception as e:
                print(f"❌ cost_analysis: {e}")
