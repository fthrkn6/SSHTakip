#!/usr/bin/env python
"""Test get_excel_path fonksiyonu"""

import os
import sys
sys.path.insert(0, os.getcwd())

from flask import Flask, session
from routes.fracas import get_excel_path

# Mock Flask app with request context
app = Flask(__name__)
app.secret_key = 'test'

with app.test_request_context():
    session['current_project'] = 'belgrad'
    path = get_excel_path()
    print(f"get_excel_path() returned: {path}")
    print(f"File exists: {os.path.exists(path) if path else 'No path'}")
    
    if path:
        print(f"File name: {os.path.basename(path)}")
