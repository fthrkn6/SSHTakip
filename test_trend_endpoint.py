import requests
import json

base_url = "http://localhost:5000"

print("\n" + "="*80)
print("AVAILABILITY TREND TEST")
print("="*80 + "\n")

periods = ['gunluk', 'haftalik', 'aylik', 'toplam']

for period in periods:
    try:
        response = requests.get(
            f"{base_url}/reports/scenarios/availability-trend",
            params={'period': period},
            cookies={'project': 'belgrad'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ {period.upper():12} | Success")
            if data.get('success'):
                trend_data = data.get('data', {})
                dates = trend_data.get('dates', [])
                averages = trend_data.get('averages', [])
                print(f"  Dates: {len(dates)} points")
                print(f"  Averages: {averages[:3]}{'...' if len(averages) > 3 else ''}")
                print(f"  Granularity: {data.get('granularity')}")
            else:
                print(f"  Error: {data.get('error')}")
        else:
            print(f"❌ {period.upper():12} | Status {response.status_code}")
    
    except Exception as e:
        print(f"❌ {period.upper():12} | {str(e)[:60]}")

print("\n" + "="*80 + "\n")
