#!/usr/bin/env python
"""Testa a renderização do template da FRACAS"""
from flask import Flask
from flask_login import LoginManager
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

# Simular login
login_manager = LoginManager()
login_manager.init_app(app)

with app.app_context():
    from routes.fracas import load_fracas_data, calculate_basic_stats, calculate_rams_metrics, calculate_pareto_analysis, calculate_trend_analysis, calculate_supplier_analysis, calculate_cost_analysis
    from flask import session, render_template
    
    with app.test_request_context():
        session['current_project'] = 'belgrad'
        
        try:
            df = load_fracas_data()
            print(f"✓ Veri yüklendi: {len(df)} satır")
            
            stats = calculate_basic_stats(df)
            rams_metrics = calculate_rams_metrics(df)
            pareto_data = calculate_pareto_analysis(df)
            trend_data = calculate_trend_analysis(df)
            supplier_data = calculate_supplier_analysis(df)
            cost_data = calculate_cost_analysis(df)
            
            print("✓ Tüm veriler hesaplandı")
            
            # Agora tente renderizar o template
            print("Tentando renderizar template...")
            html = render_template('fracas/index.html',
                                 data_available=True,
                                 data_source='Fracas_BELGRAD',
                                 stats=stats,
                                 rams=rams_metrics,
                                 pareto=pareto_data,
                                 trend=trend_data,
                                 supplier=supplier_data,
                                 cost=cost_data,
                                 total_records=len(df))
            
            print(f"✓ Template renderizado com sucesso! Tamanho: {len(html)} bytes")
            
        except Exception as e:
            print(f"❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
