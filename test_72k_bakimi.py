import requests
import json

try:
    response = requests.get('http://localhost:5000/api/bakim-plani-tablosu')
    if response.status_code == 200:
        data = response.json()
        # 72000 KM'yi bul
        item_72k = next((item for item in data if item['km'] == 72000), None)
        if item_72k:
            print('✅ 72000 KM Bakımı:')
            print(f'   Yapılacak Bakımlar: {item_72k["maintenances"]}')
            print(f'   Toplam İş: {item_72k["total_works"]}')
            print(f'   Kapsamı: {item_72k["scope_label"]}')
            print()
            print('Detaylar:')
            for m in item_72k['maintenance_detail']:
                print(f'   • {m["level"]}: {m["works"]} iş')
        else:
            print('❌ 72000 KM data bulunamadı')
    else:
        print(f'❌ API Hatası: {response.status_code}')
except Exception as e:
    print(f'❌ Bağlantı hatası: {e}')
    print('Flask çalışıyor mu? http://localhost:5000 kontrol edin')
