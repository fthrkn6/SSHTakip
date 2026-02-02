@echo off
echo ================================================
echo CMMS Baslatiliyor...
echo ================================================
echo.

REM Virtual environment kontrolu (.venv veya venv)
if exist ".venv" (
    call .venv\Scripts\activate.bat
) else if exist "venv" (
    call venv\Scripts\activate.bat
) else (
    echo HATA: Virtual environment bulunamadi!
    echo Lutfen once install_and_start.bat dosyasini calistirin.
    pause
    exit /b 1
)

REM Flask kontrolu
python -c "import flask" 2>nul
if errorlevel 1 (
    echo HATA: Flask yuklenmemis!
    echo Lutfen install_and_start.bat dosyasini calistirin.
    pause
    exit /b 1
)

echo.
echo ================================================
echo CMMS Sistemi Baslatiliyor...
echo ================================================
echo URL      : http://localhost:5000
echo Kullanici: admin
echo Sifre    : admin123
echo ================================================
echo.

REM Flask uygulamasini baslat
python app.py

pause
