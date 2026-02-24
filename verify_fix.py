#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
app.py'nin 2781 satırını kontrol et - mesaj doğru yazıyor mu?
"""
import subprocess

# 2781 satırını oku
result = subprocess.run(
    ['git', 'show', 'HEAD:app.py'],
    capture_output=True,
    text=True,
    cwd=r'c:\Users\fatiherkin\Desktop\bozankaya_ssh_takip'
)

if result.returncode == 0:
    lines = result.stdout.split('\n')
    for i in range(2775, 2785):
        if i < len(lines):
            print(f"{i+1}: {lines[i]}")
else:
    # Git yok, dosyayı direkt oku
    with open(r'c:\Users\fatiherkin\Desktop\bozankaya_ssh_takip\app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i in range(2775, min(2785, len(lines))):
            print(f"{i+1}: {lines[i]}", end='')

print("\n")
print("İSTENEN: flash(f'✅ {tram_code} KM bilgileri kaydedildi'")
