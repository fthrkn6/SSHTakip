@echo off
REM ============================================
REM Bozankaya SSH Takip - Production Start
REM ============================================

echo.
echo ========================================
echo   BOZANKAYA CMMS - Production Mode
echo ========================================
echo.

REM Önceki app'yi durdur (eğer running ise)
taskkill /F /IM python.exe 2>nul

REM Biraz bekle
timeout /t 1 /nobreak

REM Production mode'da başlat
set FLASK_ENV=production
echo ✅ FLASK_ENV = production

python app.py

pause
