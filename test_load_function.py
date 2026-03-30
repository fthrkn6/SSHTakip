#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
load_fracas_data() fonksiyonunu test et
"""
from app import create_app
from flask import session as flask_session

app = create_app()

with app.app_context():
    with app.test_request_context('/'):
        # Session'a proje kodu set et
        flask_session['current_project'] = 'belgrad'
        
        print("="* 60)
        print("TEST: load_fracas_data()")
        print("=" * 60)
        
        from routes.fracas import load_fracas_data
        
        print("\n1. Testing with project_code='belgrad'")
        df = load_fracas_data('belgrad')
        print(f"   Result: {type(df)}")
        if df is not None:
            print(f"   Rows: {len(df)}")
            print(f"   ✓ SUCCESS")
        else:
            print(f"   ✗ FAILED - df is None")
        
        print("\n2. Testing with project_code='timisoara'")
        df = load_fracas_data('timisoara')
        print(f"   Result: {type(df)}")
        if df is not None:
            print(f"   Rows: {len(df)}")
            print(f"   ✓ SUCCESS")
        else:
            print(f"   ✗ FAILED - df is None")
        
        print("\n" + "=" * 60)
