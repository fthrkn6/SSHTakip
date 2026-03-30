#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Running Flask server'a HTTP request yanında terminal loglarını görmek için
Önce server çalıştır sonra  bu test açıl ve watch logları
"""
import time
import requests

time.sleep(2)  # Server'ın başlaması için bekleme

print("Sending test requests to Flask server...")

try:
    # Test 1: Belgrad
    print("\n1. GET /fracas/?project=belgrad")
    resp = requests.get('http://localhost:5000/fracas/?project=belgrad')
    print(f"   Status: {resp.status_code}")
    print(f"   Size: {len(resp.text)} bytes")
    
    # Test 2: Timişoara
    print("\n2. GET /fracas/?project=timisoara")
    resp = requests.get('http://localhost:5000/fracas/?project=timisoara')
    print(f"   Status: {resp.status_code}")
    print(f"   Size: {len(resp.text)} bytes")
    
    print("\nRequests sent. Check server logs above.")
    
except Exception as e:
    print(f"Error: {e}")
