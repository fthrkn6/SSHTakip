import json

# maintenance.json'u yükle
with open('data/belgrad/maintenance.json', 'r', encoding='utf-8') as f:
    maintenance_data = json.load(f)

# Her bakım seviyesini km cinsine çevir
maintenance_levels = {}
for level_key, level_data in maintenance_data.items():
    km_value = level_data.get('km', 0)
    maintenance_levels[level_key] = {
        'km': km_value,
        'works': level_data.get('works', [])
    }

# Sıralı bakım listesi (KM'ye göre)
sorted_levels = sorted(maintenance_levels.items(), key=lambda x: x[1]['km'])

print("="*150)
print("📊 BAKIMLAR ARASI KM ARALIKLARINA GÖRE YAPILMASI GEREKEN BAKIMLAR")
print("="*150)
print()

# 0-300K arası tüm bakım noktalarını hesapla
max_km = 300000
maintenance_schedule = {}

for km in range(0, max_km + 1000, 1000):
    applicable_maintenances = []
    
    for level_key, level_info in sorted_levels:
        level_km = level_info['km']
        
        # Eğer km bu seviyenin katlıysa
        if km > 0 and km % level_km == 0:
            applicable_maintenances.append({
                'level': level_key,
                'km_value': level_km,
                'works_count': len([w for w in level_info['works'] if w.startswith('BOZ')])
            })
    
    if applicable_maintenances:
        maintenance_schedule[km] = applicable_maintenances

# Tablo başlığı
print()
print(f"{'KM':<8} | {'Bakım Türü':<50} | {'Toplam İş':<12} | {'Toplam Kapsamı':<15}")
print("-" * 150)

total_combined_works = 0

for km in sorted(maintenance_schedule.keys()):
    maintenances = maintenance_schedule[km]
    
    # Yapılması gereken bakımları listele
    maintenance_names = " + ".join([m['level'] + f"({m['works_count']} iş)" for m in maintenances])
    
    # Toplam iş sayısı
    total_works = sum(m['works_count'] for m in maintenances)
    
    total_combined_works = max(total_combined_works, total_works)
    
    # Seviye belirle
    if total_works >= 30:
        level = "🔴 ÇOK KAPSAMLI"
    elif total_works >= 20:
        level = "🟠 KAPSAMLI"
    elif total_works >= 10:
        level = "🟡 ORTA"
    else:
        level = "🟢 KİSMİ"
    
    print(f"{km:<8} | {maintenance_names:<50} | {total_works:<12} | {level:<15}")

print()
print("="*150)
print("📈 İSTATİSTİKLER")
print("="*150)

# İstatistikler
urgent_count = sum(1 for km, mains in maintenance_schedule.items() if sum(m['works_count'] for m in mains) >= 30)
heavy_count = sum(1 for km, mains in maintenance_schedule.items() if 20 <= sum(m['works_count'] for m in mains) < 30)
medium_count = sum(1 for km, mains in maintenance_schedule.items() if 10 <= sum(m['works_count'] for m in mains) < 20)
light_count = sum(1 for km, mains in maintenance_schedule.items() if sum(m['works_count'] for m in mains) < 10)

print(f"🔴 Çok Kapsamlı (30+ iş): {urgent_count} nok - {list(km for km, m in maintenance_schedule.items() if sum(x['works_count'] for x in m) >= 30)}")
print(f"🟠 Kapsamlı (20-29 iş): {heavy_count} nokta - {list(km for km, m in maintenance_schedule.items() if 20 <= sum(x['works_count'] for x in m) < 30)}")
print(f"🟡 Orta (10-19 iş): {medium_count} nokta - {list(km for km, m in maintenance_schedule.items() if 10 <= sum(x['works_count'] for x in m) < 20)}")
print(f"🟢 Kısmi (0-9 iş): {light_count} nokta")

print()
print("="*150)
print("💡 DETAYLAR")
print("="*150)

for km in sorted(maintenance_schedule.keys()):
    maintenances = maintenance_schedule[km]
    total = sum(m['works_count'] for m in maintenances)
    
    print(f"\n📍 {km:,} KM NOKTASI → {total} toplam iş")
    
    for m in maintenances:
        ratio = km / m['km_value']
        print(f"   • {m['level']} bakımı ({m['km_value']:,} KM × {ratio:.0f}) → {m['works_count']} iş")
