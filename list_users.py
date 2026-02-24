#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""List users in database"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    users = User.query.all()
    print(f"[Found {len(users)} users]")
    for user in users:
        print(f"  - {user.username} (email: {user.email}, role: {user.role})")
    
    # Create admin if none exists
    if not users:
        print("\n[Creating admin user...]")
        admin = User(username='admin', email='admin@admin.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin created: admin / admin123")
