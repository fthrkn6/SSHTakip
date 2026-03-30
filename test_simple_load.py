#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import create_app
from flask import session as flask_session

app = create_app()

with app.app_context():
    with app.test_request_context('/'):
        from routes.fracas import load_fracas_data
        
        print("TEST: load_fracas_data()\n")
        
        for project_code in ['belgrad', 'timisoara']:
            df = load_fracas_data(project_code)
            print(f"{project_code.upper()}:")
            if df is not None:
                print(f"  OK: Loaded {len(df)} rows")
            else:
                print(f"  FAIL: None returned")
