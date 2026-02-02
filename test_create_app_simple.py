#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Test create_app function in isolation - with detailed error handling

def main():
    print("Starting test...")
    
    try:
        print("Importing Flask...")
        from flask import Flask
        print("OK: Flask imported")
        
        print("Importing models...")
        from models import db
        print("OK: Models imported")
        
        print("Creating Flask app object...")
        app = Flask(__name__, static_folder='static', static_url_path='/static')
        print(f"OK: Flask app created: {type(app)}")
        
        print("Configuring app...")
        app.config['SECRET_KEY'] = 'test-key'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        print("OK: App configured")
        
        print("Initializing db...")
        db.init_app(app)
        print("OK: DB initialized")
        
        print("TEST PASSED: Basic setup works!")
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
