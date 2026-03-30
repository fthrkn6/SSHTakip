#!/usr/bin/env python
import sys
sys.path.insert(0, 'c:\\Users\\fatiherkin\\Desktop\\bozankaya_ssh_takip')

try:
    from routes.fracas import calculate_pareto_analysis, calculate_trend_analysis
    print("✓ Import successful")
except Exception as e:
    print(f"✗ Import error: {e}")
    import traceback
    traceback.print_exc()
