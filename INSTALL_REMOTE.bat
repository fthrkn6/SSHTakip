@echo off
REM SSH Takip Sistemi - Uzak Bilgisayar Kurulumu
REM USB veya ağ paylaşımı üzerinden yeni bilgisayara kurmak için

setlocal enabledelayedexpansion

title SSH Takip Sistemi - Uzak Kurulum

echo.
echo ====================================================
echo.  SSH TAKIP SISTEMI - UZAK BILGISAYAR KURULUMU
echo.
echo ====================================================
echo.

REM Geçerli dizini kontrol et
if not exist "app.py" (
    echo HATA: Bu dosya SSH Takip klasöründe olmalidir!
    echo.
    echo Doğru yapılış:
    echo 1. Tüm SSH Takip dosyalarını bu klasöre kopyalayın
    echo 2. Bu dosyayı (INSTALL_REMOTE.bat) klasöre kaydedin
    echo 3. Çift tıklayın
    echo.
    pause
    exit /b 1
)

REM Python kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Bu bilgisayarda Python yüklü degil!
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

echo.
echo İlk kurulum yapılıyor. Birkaç dakika sürebilir...
echo.

REM Sanal ortam oluştur
if not exist "venv" (
    echo Python sanal ortamı oluşturuluyor...
    python -m venv venv
    if errorlevel 1 (
        echo HATA: Sanal ortam oluşturulamadi!
        pause
        exit /b 1
    )
)

REM Sanal ortamı aktifleştir
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo HATA: Sanal ortam aktif olamadi!
    pause
    exit /b 1
)

REM pip güncelle
echo pip güncelleniyor...
python -m pip install --upgrade pip >nul 2>&1

REM Bağımlılıkları yükle
echo Bagimliliklar yükleniyor (bu 2-5 dakika sürebilir)...
pip install -r requirements.txt
if errorlevel 1 (
    echo HATA: Bagimliliklar yuklenemedi!
    echo Ağ bağlantınızı kontrol edin ve tekrar deneyin.
    pause
    exit /b 1
)

echo.
echo ====================================================
echo.
echo  KURULUM BASARILI!
echo.
echo ====================================================
echo.

echo SSH Takip Sistemi artık bu bilgisayarda hazır.
echo.

REM Başlatma seçeneğini sor
echo Şimdi uygulamayı başlatmak istiyor musunuz? (E/H)
set /p choice="Seçim: "

if /i "%choice%"=="E" (
    echo.
    echo Uygulama baslatiliyor...
    echo Tarayıcı otomatik acılacak.
    echo.
    timeout /t 2 /nobreak >nul
    start http://localhost:5000
    python app.py
) else (
    echo.
    echo Kurulum tamamlandı!
    echo.
    echo Uygulamayı başlatmak için:
    echo - RUN_SSH_TAKIP.bat dosyasını çift tıklayın
    echo.
    echo Ya da komut satırında:
    echo   cd C:\SSH_Takip
    echo   venv\Scripts\activate
    echo   python app.py
    echo.
    pause
)
