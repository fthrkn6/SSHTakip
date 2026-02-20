#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Veritabanı reset scripti"""

from app import create_app, db

app = create_app()

with app.app_context():
    print("🔄 Veritabanı sıfırlanıyor...")
    db.drop_all()
    print("✓ Eski tablolar silindi")
    
    db.create_all()
    print("✓ Yeni tablolar oluşturuldu")
    print("✓ ServiceStatus'e project_code sütunu eklendi")
    print("\n✨ Veritabanı yenilendi ve hazır!")
