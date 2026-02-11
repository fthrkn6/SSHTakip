from app import create_app
import json

app = create_app()
client = app.test_client()

# API test et
response = client.get('/api/bakim-verileri')
print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    data = response.get_json()
    tramps = data.get('tramps', [])
    levels = data.get('levels', [])
    
    print(f"✅ Araç Sayısı: {len(tramps)}")
    print(f"✅ Bakım Seviyeleri: {', '.join(levels)}\n")
    
    if tramps:
        tram = tramps[0]
        print(f"İlk Araç: {tram['tram_name']} ({tram['current_km']} km)\n")
        
        print("Bakım Durumları:")
        for level in levels:
            m = tram['maintenance'].get(level)
            if m:
                icon = {'normal': '🟢', 'warning': '🟡', 'urgent': '🔴', 'overdue': '⚫'}.get(m['status'], '·')
                print(f"  {icon} {level}: {m['km_left']:>6.0f} km kaldı ({m['required_km']} km)")
else:
    print(f"❌ API Hatası: {response.status_code}")
