from app import create_app

app = create_app()
client = app.test_client()

response = client.get('/api/bakim-verileri')

if response.status_code == 200:
    data = response.get_json()
    tramps = data.get('tramps', [])
    levels = data.get('levels', [])
    
    print("📊 BAKIM DURUM TABLOSUю\n")
    print(f"{'Araç':<10} | {'KM':<8} | 60K Status")
    print("-" * 50)
    
    for tram in tramps[:10]:
        m60k = tram['maintenance'].get('60K')
        if m60k:
            status_icon = {'normal': '🟢', 'warning': '🟡', 'urgent': '🔴', 'overdue': '⚫'}.get(m60k['status'], '·')
            status_text = m60k['status']
            km_left = m60k['km_left']
            
            print(f"{tram['tram_name']:<10} | {tram['current_km']:<8} | {status_icon} {status_text:<10} ({km_left:.0f} km)")
