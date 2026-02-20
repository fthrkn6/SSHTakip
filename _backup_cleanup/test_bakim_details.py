from app import create_app
import json

app = create_app()
client = app.test_client()

# API test et
response = client.get('/api/bakim-verileri')

if response.status_code == 200:
    data = response.get_json()
    tramps = data.get('tramps', [])
    levels = data.get('levels', [])
    
    print("🔍 KM'ye Göre Bakım Durumları\n")
    
    # Farklı KM'deki araçları bul
    test_tramps = [
        (1531, 1500),    # Henüz başlamadı (6K'ye 4500 km kaldı)
        (1532, 7500),    # 6K'yi geçmiş, 18K'ye yaklaştı
        (1533, 25000),   # İki bakımı geçmiş
    ]
    
    for tram in tramps:
        tram_km = tram['current_km']
        if tram_km in [k for _, k in test_tramps]:
            print(f"\n📍 {tram['tram_name']} | {tram_km:>6} km =>")
            
            for level in levels[:5]:  # İlk 5 bakımı göster
                m = tram['maintenance'].get(level)
                if m:
                    status_icon = {'normal': '✓  ', 'warning': '⚠  ', 'urgent': '🔴 ', 'overdue': '✘  '}[m['status']]
                    
                    # Yapılması gereken katları bul
                    level_km = int(level.replace('K', '')) * 1000
                    completed = []
                    for mult in range(1, 15):
                        cat_km = level_km * mult
                        if cat_km <= tram_km:
                            completed.append(f"{mult}x")
                    
                    next_km = m['required_km']
                    
                    print(f"  {status_icon} {level:5} | Yapılan: {','.join(completed) or '-':15} | Sonraki: {next_km:>6} km | {m['km_left']:>6.0f} km kaldı")
            
            break  # Sadece ilk uygun araçı göster
