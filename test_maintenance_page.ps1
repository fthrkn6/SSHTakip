#!/usr/bin/env powershell

# App'ı başlat
$appProcess = Start-Process -FilePath "python" -ArgumentList "app.py" -PassThru -NoNewWindow

# Biraz bekle
Start-Sleep -Seconds 3

# Browser aç
Start-Process "http://localhost:5000/bakim-planlari"

Write-Host "App başlatıldı. Localhost:5000/bakim-planlari sayfasını açtığınızda bakım planlama sayfasını göreceksiniz."
Write-Host "Ctrl+C ile kapatmak için Terminal'de kill komutu kullanın: $($appProcess.Id)"
