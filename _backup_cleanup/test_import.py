#!/usr/bin/env python
"""Test script to identify import and initialization errors"""

import sys
import traceback

print("=" * 80)
print("TESTING APP INITIALIZATION")
print("=" * 80)

try:
    print("\n1. Importing app.py...")
    from app import create_app, init_sample_data
    print("   ✅ Import successful")
    
    print("\n2. Creating Flask app...")
    app = create_app()
    if app is None:
        print("   ❌ create_app() returned None")
        sys.exit(1)
    print("   ✅ App created successfully")
    
    print("\n3. Testing app context...")
    with app.app_context():
        print("   ✅ App context created")
        
        print("\n4. Initializing sample data...")
        init_sample_data(app)
        print("   ✅ Sample data initialized")
    
    print("\n5. Testing route registration...")
    print(f"   Total routes registered: {len(app.url_map._rules)}")
    for rule in list(app.url_map.iter_rules())[:10]:
        print(f"     - {rule.endpoint}: {rule.rule}")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    print(f"\nFull Traceback:")
    traceback.print_exc()
    print("=" * 80)
    sys.exit(1)
