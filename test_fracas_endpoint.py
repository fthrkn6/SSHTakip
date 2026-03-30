from app import create_app
from flask import session

app = create_app()

with app.app_context():
    with app.test_client() as client:
        print("=" * 60)
        print("TEST: FRACAS ENDPOINT")
        print("=" * 60)
        
        # Test endpoint without login (should redirect to login)
        print("\n1. Belgrad /fracas/ (no login):")
        response = client.get('/fracas/', follow_redirects=False)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print(f"   Redirects to: {response.location}")
        
        print("\n2. Checking response data...")
        response = client.get('/fracas/', follow_redirects=True)
        print(f"   Total response length: {len(response.data)} bytes")
        
        # Check for canvas elements
        checks = [
            (b'paretoModuleChart', 'Canvas paretoModuleChart'),
            (b'paretoSupplierChart', 'Canvas paretoSupplierChart'),
            (b'monthlyTrendChart', 'Canvas monthlyTrendChart'),
            (b'data_available', 'data_available variable'),
            (b'new Chart', 'Chart.js init code'),
            (b'alert', 'Alert element'),
            (b'Veri Yok', 'No data message'),
        ]
        
        print("\n3. Content checks:")
        for bytesearch, label in checks:
            exists = bytesearch in response.data
            symbol = '✓' if exists else '✗'
            print(f"   {symbol} {label}")
