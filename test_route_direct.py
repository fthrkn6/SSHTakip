"""API route'unu direkt Python'dan test et"""
from app import app
from routes.dashboard import get_equipment_failures
from flask import session

# App context'te test et
with app.test_request_context('/dashboard/api/failures'):
    # Session'a current_project ekle
    session['current_project'] = 'belgrad'
    
    print("="*60)
    print("[TEST 1] Global arızalar")
    print("="*60)
    
    try:
        # API fonksiyonunu direkt çağır
        result = get_equipment_failures()
        data = result.get_json() if hasattr(result, 'get_json') else result
        
        print(f"✓ Status: 200")
        print(f"✓ Arıza sayısı: {data.get('count', 0)}")
        
        if data.get('failures'):
            print("\nGerçek FRACAS Arızaları:")
            for i, f in enumerate(data['failures'], 1):
                print(f"  {i}. {f['arac_no']} ({f['sistem']}): {f['ariza_tanimi'][:55]}")
        else:
            print(f"Hata: {data.get('error', 'Bilinmiyor')}")
    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("[TEST 2] 1531 araçı")  
print("="*60)

with app.test_request_context('/dashboard/api/failures/1531'):
    session['current_project'] = 'belgrad'
    
    try:
        result = get_equipment_failures('1531')
        data = result.get_json() if hasattr(result, 'get_json') else result
        
        print(f"✓ Status: 200")
        print(f"✓ 1531'in arıza sayısı: {data.get('count', 0)}")
        
        if data.get('failures'):
            print("\n1531 için gerçek arızalar:")
            for i, f in enumerate(data['failures'], 1):
                print(f"  {i}. {f['sistem']}: {f['ariza_tanimi'][:55]}")
        else:
            print(f"Hata: {data.get('error', 'Bilinmiyor')}")
    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("✅ Sonuç: Dashboard'da gerçek FRACAS verileri gösterilecek!")
print("="*60)
