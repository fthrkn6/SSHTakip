import subprocess
import json

print("[INFO] Tüm commit'lerde KM veri sayısı kontrol ediliyor...")

# Git log'unu al
result = subprocess.run(
    ['git', 'log', '--oneline', 'data/belgrad/km_data.json'],
    capture_output=True,
    text=True
)

commits = [line.split()[0] for line in result.stdout.strip().split('\n') if line]

for commit in commits[:10]:  # İlk 10 commit'i kontrol et
    result = subprocess.run(
        ['git', 'show', f'{commit}:data/belgrad/km_data.json'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            count = len(data)
            has_data = sum(1 for k, v in data.items() if k and v.get('current_km', 0) > 0)
            print(f"  {commit}: {count} items, {has_data} with KM > 0")
            
            if has_data > 10:
                print(f"[FOUND] {commit} has most data!")
                break
        except:
            pass
