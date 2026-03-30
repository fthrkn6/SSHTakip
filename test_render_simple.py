#!/usr/bin/env python
"""Template render test"""
import sys
sys.path.insert(0, '.')

from flask import Flask, session
from routes.fracas import load_fracas_data, calculate_basic_stats, calculate_rams_metrics, calculate_pareto_analysis, calculate_trend_analysis, calculate_supplier_analysis, calculate_cost_analysis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'

with app.app_context():
    with app.test_request_context():
        session['current_project'] = 'belgrad'
        df = load_fracas_data()
        
        stats = calculate_basic_stats(df)
        rams = calculate_rams_metrics(df)
        pareto = calculate_pareto_analysis(df)
        trend = calculate_trend_analysis(df)
        supplier = calculate_supplier_analysis(df)
        cost = calculate_cost_analysis(df)
        
        try:
            html = app.jinja_env.get_template('fracas/index.html').render(
                data_available=True,
                data_source='Test',
                stats=stats,
                rams=rams,
                pareto=pareto,
                pareto_labels_module=[],
                pareto_counts_module=[],
                pareto_cumulative_module=[],
                pareto_labels_supplier=[],
                pareto_counts_supplier=[],
                pareto_cumulative_supplier=[],
                pareto_labels_location=[],
                pareto_counts_location=[],
                pareto_cumulative_location=[],
                pareto_labels_class=[],
                pareto_counts_class=[],
                pareto_cumulative_class=[],
                trend_periods=[],
                trend_counts=[],
                trend_hours=[],
                trend_hour_counts=[],
                trend_days=[],
                trend_day_counts=[],
                trend=trend,
                supplier=supplier,
                cost=cost,
                total_records=len(df)
            )
            print("✅ Template render OK!")
            print(f"HTML: {len(html)} karakter")
        except Exception as e:
            print(f"❌ Template error: {e}")
            import traceback
            traceback.print_exc()
