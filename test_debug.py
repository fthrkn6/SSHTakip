"""Debug servis durumu verilerini test et"""
import pandas as pd
import json
from datetime import date, timedelta

# Parametreler
project = 'belgrad'

# Tram listesini yükle
df = pd.read_excel(f'data/{project}/trams.xlsx')
tram_list = df['tram_id'].dropna().tolist()
tram_list.sort(key=lambda x: int(x) if str(x).isdigit() else 0)
print(f"Toplam araç: {len(tram_list)}")
print(f"İlk 3 araç: {tram_list[:3]}")

# Status yükle
with open(f'data/{project}/service_status.json', 'r', encoding='utf-8') as f:
    status_data = json.load(f)
print(f"Status keys: {list(status_data.keys())[:5]}")

# Son 7 günü hesapla
today = date.today()
today_str = today.strftime('%Y-%m-%d')
last_7_days = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
print(f"Bugün: {today_str}")
print(f"Son 7 gün: {last_7_days}")

# Tramvaylar listesini oluştur (app.py'deki gibi)
tramvaylar = []
for tram_id in tram_list:
    tram_str = str(tram_id)
    tram_status = status_data.get(tram_str, {})
    
    # Son 7 günlük durumları al
    weekly_status = {}
    for day in last_7_days:
        day_data = tram_status.get(day, {})
        weekly_status[day] = day_data.get('status', 'bilinmiyor')
    
    # Bugünkü durum
    current_status = tram_status.get(today_str, {}).get('status', 'bilinmiyor')
    
    tramvaylar.append({
        'id': tram_id,
        'current_status': current_status,
        'weekly_status': weekly_status,
    })

# İlk tramvayın verilerini göster
print("\n=== İlk tramvay verisi ===")
first = tramvaylar[0]
print(f"ID: {first['id']}")
print(f"Current status: {first['current_status']}")
print(f"Weekly status:")
for day, status in first['weekly_status'].items():
    marker = " <-- BUGÜN" if day == today_str else ""
    print(f"  {day}: {status}{marker}")
