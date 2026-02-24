#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
App initialize hatalarını bul
"""
import sys
import traceback

print("\n" + "="*80)
print("CREATE_APP HATA TESPITI")
print("="*80 + "\n")

try:
    # app.py'yi import et
    print("Step 1: Importing app.py...")
    from app import create_app
    print(f"  [OK] create_app function imported")
    
    # create_app() çağır
    print("\nStep 2: Calling create_app()...")
    app = create_app()
    
    if app is None:
        print("  [ERROR] create_app() returned None")
        print("  -> Hatanin causa create_app() cikisinda kaptı ve None dondurdu")
    else:
        print(f"  [OK] app created: {type(app)}")
        with app.app_context():
            print(f"  [OK] app context works")

except Exception as e:
    print(f"\n[ERROR]: {type(e).__name__}")
    print(f"Message: {e}")
    print("\nTraceback:")
    traceback.print_exc()

print("\n" + "="*80 + "\n")
