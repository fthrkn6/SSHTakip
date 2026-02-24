#!/usr/bin/env python
"""Test script for permissions page"""

from app import create_app
from models import db, User
import sys

app = create_app()

# Test 1: Check if route exists
print("\n=== TEST 1: Check if route exists ===")
with app.app_context():
    rules = [rule.rule for rule in app.url_map.iter_rules() if 'permission' in rule.rule]
    if rules:
        print(f"✓ Found permissions routes: {rules}")
    else:
        print("✗ No permissions routes found")

# Test 2: Check database and template
print("\n=== TEST 2: Check database users ===")
with app.app_context():
    users = User.query.all()
    print(f"✓ Total users in database: {len(users)}")
    for user in users[:5]:
        projects = user.get_assigned_projects() if hasattr(user, 'get_assigned_projects') else []
        print(f"  - {user.username} (Role: {user.role}, Projects: {projects})")

# Test 3: Check if template exists
print("\n=== TEST 3: Check if template exists ===")
import os
template_path = 'templates/admin/permissions.html'
if os.path.exists(template_path):
    print(f"✓ Template file exists: {template_path}")
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'Rol ve Yetki' in content:
            print("✓ Template contains page title")
        if 'assigned_projects' in content:
            print("✓ Template contains assigned_projects references")
        if 'admin.update_user_role' in content:
            print("✓ Template contains role update form action")
else:
    print(f"✗ Template file not found: {template_path}")

# Test 4: Check routes decorators
print("\n=== TEST 4: Check route details ===")
with app.app_context():
    for rule in app.url_map.iter_rules():
        if 'permission' in rule.rule:
            print(f"✓ Route: {rule.rule}")
            print(f"  Methods: {rule.methods}")
            print(f"  Endpoint: {rule.endpoint}")

print("\n=== TEST COMPLETE ===\n")

