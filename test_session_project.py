from flask import session
from app import create_app
import tempfile
import os

app = create_app()

# Test 1: Check session default project
print("TEST 1: Session proje seçimi")
with app.app_context():
    with app.test_request_context():
        print(f"  current_project (boş session): {session.get('current_project', 'DEFAULT=BELGRAD')}")
        
        # Simulate selecting Timişoara
        session['current_project'] = 'timisoara'
        session.modified = True
        print(f"  current_project (timisoara set): {session.get('current_project')}")

print()

# Test 2: Check if route loads correct data based on session
print("TEST 2: Route davranışı")
with app.app_context():
    with app.test_client() as client:
        # First, try accessing /fracas without session
        print("  /fracas (boş session):")
        # Will redirect to login
        resp = client.get('/fracas/', follow_redirects=False)
        print(f"    Status: {resp.status_code} {resp.location if resp.status_code >= 300 else 'OK'}")
        
print()
print("SONUÇ: Issue session'da current_project set edilmediği için olabilir!")
