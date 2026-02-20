#!/usr/bin/env python3
"""Check registered routes in Flask app"""

from app import create_app

app = create_app()

print("=== REGISTERED ROUTES ===\n")
for rule in app.url_map.iter_rules():
    print(f"{rule.rule:50} -> {rule.endpoint:30} {rule.methods}")
