#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import traceback

try:
    print("Test starting...")
    from app import create_app
    print("create_app imported")
    
    app = create_app()
    print(f"app type: {type(app)}")
    
    if app:
        print("OK: App created successfully")
    else:
        print("ERROR: App is None")
except Exception as e:
    print(f"\nERROR OCCURRED:")
    traceback.print_exc()
