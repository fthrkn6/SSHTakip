"""API'yi direkt test et - app context içinde (login gerekmiyor)"""
from app import app
from flask import session

with app.test_client() as client:
    print("API Testing (Direct)...")
    print("="*60)
    
    # Test 1: Global arızalar
    print("\n[TEST 1] GET /dashboard/api/failures")
    try:
        # Session'da current_project'i set et
        with client.session_transaction() as sess:
            sess['current_project'] = 'belgrad'
            sess['user_id'] = 1  # Test user
        
        # API'yi çağır
        response = client.get('/dashboard/api/failures')
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 401]:
            data = response.get_json()
            
            if data.get('failures'):
                print(f"✓ Arıza sayısı: {len(data['failures'])}")
                print("\nArızalar:")
                for f in data['failures']:
                    print(f"  - {f['arac_no']} ({f['sistem']}): {f['ariza_tanimi'][:50]}")
            else:
                print(f"Hata: {data.get('error', 'Bilinmiyor')}")
        else:
            print(f"HTTP Hatası: {response.data}")
    except Exception as e:
        print(f"Test 1 hatası: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: 1531 araçı
    print("\n[TEST 2] GET /dashboard/api/failures/1531")
    try:
        with client.session_transaction() as sess:
            sess['current_project'] = 'belgrad'
            sess['user_id'] = 1
        
        response = client.get('/dashboard/api/failures/1531')
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 401]:
            data = response.get_json()
            
            if data.get('failures'):
                print(f"✓ 1531'in arıza sayısı: {len(data['failures'])}")
                print("\n1531'in arızaları:")
                for f in data['failures']:
                    print(f"  - {f['sistem']}: {f['ariza_tanimi'][:60]}")
            else:
                print(f"Hata: {data.get('error', 'Bilinmiyor')}")
    except Exception as e:
        print(f"Test 2 hatası: {e}")

print("\n" + "="*60)
print("✅ API Test tamamlandı!")
