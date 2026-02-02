@echo off
echo ================================================
echo CMMS Kurulum ve Baslatma
echo ================================================
echo.

REM Python versiyonunu kontrol et
python --version
if errorlevel 1 (
    echo HATA: Python bulunamadi!
    echo Lutfen Python 3.8 veya ustunu yukleyin.
    pause
    exit /b 1
)

echo.
echo [1/5] Virtual environment olusturuluyor...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment olusturuldu.
) else (
    echo Virtual environment zaten mevcut.
)

echo.
echo [2/5] Virtual environment aktiflestiriliryor...
call venv\Scripts\activate.bat

echo.
echo [3/5] Pip guncelleniyor...
python -m pip install --upgrade pip

echo.
echo [4/5] Temel paketler yukleniyor (bu biraz zaman alabilir)...
pip install Flask==3.0.0
pip install Flask-SQLAlchemy==3.1.1
pip install Flask-Login==0.6.3
pip install Flask-Migrate==4.0.5
pip install python-dotenv==1.0.0
pip install requests==2.31.0
pip install Werkzeug==3.0.0
pip install cryptography==41.0.7

echo.
echo Opsiyonel paketler yukleniyor...
pip install APScheduler==3.10.4

echo.
echo [5/5] Veritabani ve ornek veri olusturuluyor...
if not exist "cmms.db" (
    python create_sample_data.py
) else (
    echo Veritabani zaten mevcut. Yeniden olusturmak icin cmms.db dosyasini silin.
)

echo.
echo ================================================
echo KURULUM TAMAMLANDI!
echo ================================================
echo.
echo Giris Bilgileri:
echo ----------------
echo URL      : http://localhost:5000
echo Kullanici: admin
echo Sifre    : admin123
echo ================================================
echo.

echo Uygulama baslatiliyor...
echo.
python app.py

pause
