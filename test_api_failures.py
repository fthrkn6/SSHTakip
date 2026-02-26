"""API test - Excel arıza verileri"""
import requests
import json
from app import app

app.config['TESTING'] = True

with app.test_client() as client:
    # Login gerekli değil test için ama session test edelim
    print("Testing /dashboard/api/failures endpoints...\n")
    
    # Test 1: Global son 5 arıza
    try:
        with client:
            # Session'da current_project'i set et
            with client.session_transaction() as sess:
                sess['current_project'] = 'belgrad'
            
            # API'yi çağır
            response = client.get('/dashboard/api/failures')
            data = response.get_json()
            
            print(f"[TEST 1] Global son 5 arıza")
            print(f"Status: {response.status_code}")
            print(f"Arıza sayısı: {data.get('count', 0)}")
            if data.get('failures'):
                print("Arızalar:")
                for f in data['failures'][:3]:
                    print(f"  - {f.get('fracas_id')} ({f.get('arac_no')}): {f.get('ariza_tanimi')}")
            else:
                print("Hata:", data.get('error', 'Arıza bulunamadı'))
                
    except Exception as e:
        print(f"[ERROR] Test 1: {e}")
    
    # Test 2: Specific araç (1531)
    print("\n[TEST 2] 1531 araçı için arızalar")
    try:
        with client:
            with client.session_transaction() as sess:
                sess['current_project'] = 'belgrad'
            
            response = client.get('/dashboard/api/failures/1531')
            data = response.get_json()
            
            print(f"Status: {response.status_code}")
            print(f"Arıza sayısı: {data.get('count', 0)}")
            if data.get('failures'):
                print("1531'in arızaları:")
                for f in data['failures']:
                    print(f"  - {f.get('fracas_id')}: {f.get('ariza_tanimi')}")
            else:
                print("Hata:", data.get('error', 'Arıza bulunamadı'))
    except Exception as e:
        print(f"[ERROR] Test 2: {e}")
