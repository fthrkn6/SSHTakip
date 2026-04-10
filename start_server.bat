@echo off
title SSH Takip v2.1 - Server
cd /d %~dp0

echo ============================================
echo   SSH Takip v2.1 - Bozankaya
echo   Server baslatiliyor...
echo ============================================
echo.

REM Virtual environment aktiflestir
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [HATA] Virtual environment bulunamadi!
    echo Once kurulum yapin: python -m venv venv
    pause
    exit /b 1
)

REM Waitress kurulu mu kontrol et
python -c "import waitress" 2>nul
if errorlevel 1 (
    echo [INFO] Waitress kuruluyor...
    pip install waitress
)

echo.
echo [OK] Server baslatiliyor: http://0.0.0.0:5000
echo [OK] Durdurmak icin: Ctrl+C
echo.

python -m waitress --host=0.0.0.0 --port=5000 --threads=4 "app:create_app()"

pause
