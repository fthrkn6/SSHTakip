@echo off
echo Temizlik yapiliyor...

REM Virtual environment
if exist "venv" (
    echo Virtual environment siliniyor...
    rmdir /s /q venv
)

REM Veritabani
if exist "cmms.db" (
    echo Veritabani siliniyor...
    del cmms.db
)

REM Python cache
if exist "__pycache__" (
    echo Cache temizleniyor...
    rmdir /s /q __pycache__
)

for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

REM .pyc dosyalari
del /s /q *.pyc 2>nul

echo.
echo Temizlik tamamlandi!
echo Yeniden baslatmak icin: install_and_start.bat
echo.
pause
