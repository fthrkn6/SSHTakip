@echo off
REM SSH Takip Sistemi - Tek Tik Baslatma
REM Bu dosyayı SSH Takip klasöründe kaydedin ve çift tıklayın

setlocal enabledelayedexpansion

REM Renk tanımları (Windows 10+)
cls
title SSH Takip Sistemi - Baslatma

echo.
echo ====================================================
echo.  SSH TAKIP SISTEMI - BASLATICI
echo.
echo ====================================================
echo.

REM Geçerli dizini kontrol et
if not exist "app.py" (
    echo HATA: Bu dosya SSH Takip klasöründe olmalidir!
    echo Kontrol Edin: app.py dosyasi var mi?
    pause
    exit /b 1
)

REM Python kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python yüklü degil!
    echo.
    echo Çözüm:
    echo 1. Python 3.8+ yükleyin: https://www.python.org
    echo 2. Kurulum sırasında "Add Python to PATH" seçin
    echo 3. Bilgisayarı yeniden başlatın
    echo 4. Bu dosyayı tekrar çalıştırın
    echo.
    pause
    exit /b 1
)

REM Sanal ortam oluştur (eğer yoksa)
if not exist "venv" (
    echo [1/4] Sanal ortam olusturuluyor...
    python -m venv venv
    echo      ✓ Sanal ortam hazır
    echo.
)

REM Sanal ortamı aktifleştir
echo [2/4] Sanal ortam aktifleştiriliyor...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo HATA: Sanal ortam aktif olamadi!
    pause
    exit /b 1
)
echo      ✓ Sanal ortam aktif
echo.

REM Bağımlılıkları yükle
echo [3/4] Bagimliliklar yükleniyor...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo HATA: Bagimliliklar yuklenemedi!
    echo Detaylar için:
    pip install -r requirements.txt
    pause
    exit /b 1
)
echo      ✓ Bagimliliklar hazır
echo.

REM Tarayıcı açmaya çalış
echo [4/4] Uygulama baslatiliyor...
timeout /t 1 /nobreak >nul
start http://localhost:5000
echo      ✓ Tarayıcı acılıyor
echo.

echo ====================================================
echo.
echo  UYGULAMA BASLATILDI!
echo.
echo  Erişim Adresi: http://localhost:5000
echo.
echo  Giriş Bilgileri:
echo  - Kullanıcı Adı: admin
echo  - Şifre: admin123
echo.
echo  Başka Bilgisayardan Erişim:
echo  Aynı Ağda İseniz: http://[BU-BİLGİSAYARIN-IP]:5000
echo  IP'ni bulmak için komut satırında: ipconfig
echo.
echo  Penceyi Kapatmak = Uygulamayı Durdur
echo.
echo ====================================================
echo.

REM Uygulamayı çalıştır
python app.py

REM Uygulama kapatıldığında
echo.
echo SSH Takip Sistemi durduruldu.
echo.
pause
