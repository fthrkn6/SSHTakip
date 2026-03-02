from app import app
import json

with app.test_client() as client:
    # /api/projects endpoint'ini test et
    response = client.get('/api/projects')
    print(f"Status: {response.status_code}")
    print(f"Data: {response.data.decode()}")
