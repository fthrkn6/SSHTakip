import requests
import json
from datetime import date, timedelta

base_url = "http://localhost:5000"

print(f"\n{'='*80}")
print(f"KAYSERI PROJESİ - AVAILABILITY TEST")
print(f"{'='*80}\n")

# Test periods
periods = ['gunluk', 'haftalik', 'aylik', 'toplam']

for period in periods:
    try:
        response = requests.get(
            f"{base_url}/reports/scenarios/data",
            params={'period': period},
            cookies={'project': 'kayseri'},  # Kayseri projesini seç
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ {period.upper():10} | Success")
            if data.get('data'):
                # İlk 3 araç göster
                items = list(data['data'].items())[:3]
                for equipment, availability in items:
                    print(f"  - {equipment}: {availability}%")
                if len(data['data']) > 3:
                    print(f"  ... +{len(data['data']) - 3} more")
            else:
                print(f"  ⚠️  No data returned")
            print(f"  Date range: {data.get('date_range')}")
        else:
            print(f"❌ {period.upper():10} | Status {response.status_code}")
            print(f"  Error: {response.text[:100]}")
    
    except requests.exceptions.ConnectionError:
        print(f"❌ {period.upper():10} | Cannot connect to Flask (http://localhost:5000)")
        break
    except Exception as e:
        print(f"❌ {period.upper():10} | Error: {str(e)[:60]}")
    
    print()

print(f"{'='*80}\n")
