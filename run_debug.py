#!/usr/bin/env python
"""Run Flask app with debug mode enabled"""
import os
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

from app import create_app

app = create_app()
app.run(debug=True, host='0.0.0.0', port=5000)
