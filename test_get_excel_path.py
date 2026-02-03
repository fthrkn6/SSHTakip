#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from flask import session

app = create_app()

# Test edelim
with app.test_request_context():
    from routes.fracas import get_excel_path
    
    # Session boş olsa da
    print("=== get_excel_path() TEST ===\n")
    
    excel_path = get_excel_path()
    print(f"Döndürülen path: {excel_path}")
    
    if excel_path:
        print(f"  → Dosya var: {os.path.exists(excel_path)}")
        print(f"  → Dosya adı: {os.path.basename(excel_path)}")
    else:
        print("  → PATH YOK (None döndürüldü)")
