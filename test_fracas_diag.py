"""FRACAS render diagnostik - auth bypass ile template render test"""
import os, sys, io
sys.path.insert(0, os.path.dirname(__file__))
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app

app = create_app()

with app.app_context():
    # 1. Veri yukle
    from routes.fracas import load_fracas_data, calculate_pareto_analysis, calculate_basic_stats, calculate_trend_analysis
    
    for project in ['belgrad', 'timisoara']:
        print(f"\n{'='*60}")
        print(f"PROJE: {project.upper()}")
        print(f"{'='*60}")
        
        df = load_fracas_data(project)
        if df is None:
            print(f"HATA: load_fracas_data({project}) None dondu!")
            continue
        
        print(f"Satir sayisi: {len(df)}")
        print(f"Kolonlar: {list(df.columns[:5])}...")
        
        stats = calculate_basic_stats(df)
        pareto = calculate_pareto_analysis(df)
        trend = calculate_trend_analysis(df)
        
        # Template'e gonderilen degiskenler
        pareto_labels_module = [item['name'][:20] for item in pareto['by_module']]
        pareto_counts_module = [item['count'] for item in pareto['by_module']]
        pareto_cumulative_module = [item['cumulative'] for item in pareto['by_module']]
        
        pareto_labels_supplier = [item['name'][:20] for item in pareto['by_supplier']]
        pareto_counts_supplier = [item['count'] for item in pareto['by_supplier']]
        
        trend_periods = [item['period'] for item in trend['monthly']]
        trend_counts = [item['count'] for item in trend['monthly']]
        
        print(f"\npareto_labels_module = {pareto_labels_module}")
        print(f"pareto_counts_module = {pareto_counts_module}")
        print(f"pareto_labels_supplier = {pareto_labels_supplier[:3]}...")
        print(f"trend_periods = {trend_periods[:3]}...")
        print(f"trend_counts = {trend_counts[:3]}...")
        
        # 2. Template render test - flask render_template_string ile
        from flask import render_template_string
        
        # Basit test: tojson ciktisi
        test_tpl = """{{ labels|tojson }}"""
        result = render_template_string(test_tpl, labels=pareto_labels_module)
        print(f"\ntojson test: {result[:100]}")
        
        # 3. Asil template'i render et  
        from flask import render_template
        
        # Mock login_required bypass - request context ile  
        with app.test_request_context('/fracas/?project=' + project):
            from flask_login import AnonymousUserMixin
            from flask import g
            # Mock current_user
            
            pareto_labels_location = [item['name'][:25] for item in pareto['by_location']]
            pareto_counts_location = [item['count'] for item in pareto['by_location']]
            pareto_cumulative_location = [item['cumulative'] for item in pareto['by_location']]
            
            pareto_labels_class = [item['name'][:30] for item in pareto['by_failure_class']]
            pareto_counts_class = [item['count'] for item in pareto['by_failure_class']]
            pareto_cumulative_class = [item['cumulative'] for item in pareto['by_failure_class']]
            
            trend_hours = [item['hour'] for item in trend['by_hour']]
            trend_hour_counts = [item['count'] for item in trend['by_hour']]
            trend_days = [item['day'] for item in trend['by_weekday']]
            trend_day_counts = [item['count'] for item in trend['by_weekday']]
            
            from routes.fracas import calculate_rams_metrics, calculate_supplier_analysis, calculate_cost_analysis
            rams_metrics = calculate_rams_metrics(df)
            supplier_data = calculate_supplier_analysis(df)
            cost_data = calculate_cost_analysis(df)
            
            try:
                html = render_template('fracas/index.html',
                    data_available=True,
                    data_source=f'Fracas_{project.upper()}',
                    stats=stats,
                    rams=rams_metrics,
                    pareto=pareto,
                    pareto_labels_module=pareto_labels_module,
                    pareto_counts_module=pareto_counts_module,
                    pareto_cumulative_module=pareto_cumulative_module,
                    pareto_labels_supplier=pareto_labels_supplier,
                    pareto_counts_supplier=pareto_counts_supplier,
                    pareto_cumulative_supplier=[item['cumulative'] for item in pareto['by_supplier']],
                    pareto_labels_location=pareto_labels_location,
                    pareto_counts_location=pareto_counts_location,
                    pareto_cumulative_location=pareto_cumulative_location,
                    pareto_labels_class=pareto_labels_class,
                    pareto_counts_class=pareto_counts_class,
                    pareto_cumulative_class=pareto_cumulative_class,
                    trend_periods=trend_periods,
                    trend_counts=trend_counts,
                    trend_hours=trend_hours,
                    trend_hour_counts=trend_hour_counts,
                    trend_days=trend_days,
                    trend_day_counts=trend_day_counts,
                    trend=trend,
                    supplier=supplier_data,
                    cost=cost_data,
                    total_records=len(df))
                
                print(f"\nTemplate RENDER BASARILI! HTML boyutu: {len(html)} bytes")
                
                # Kontroller
                checks = {
                    'paretoModuleChart canvas': 'paretoModuleChart' in html,
                    'paretoSupplierChart canvas': 'paretoSupplierChart' in html,
                    'monthlyTrendChart canvas': 'monthlyTrendChart' in html,
                    'new Chart call': 'new Chart' in html,
                    'chart.js CDN': 'chart.js' in html,
                    'Excel uyari (data_available=False)': 'Excel Dosyası Bulunamadı' in html,
                    'Filtreler paneli': 'Filtreler' in html,
                }
                
                print("\n--- RENDER KONTROLLERI ---")
                for desc, result in checks.items():
                    status = "OK" if result else "FAIL"
                    print(f"  [{status}] {desc}")
                
                # HTML dosyaya kaydet
                fname = f'fracas_rendered_{project}.html'
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"\nHTML kaydedildi: {fname}")
                
            except Exception as e:
                print(f"\nTEMPLATE RENDER HATASI: {e}")
                import traceback
                traceback.print_exc()
