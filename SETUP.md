# SSH Takip Sistemi - Kurulum Rehberi

## 📋 İçindekiler
1. [Sistem Gereksinimleri](#sistem-gereksinimleri)
2. [Kurulum Adımları](#kurulum-adımları)
3. [Yerel Ağda Kullanım](#yerel-ağda-kullanım)
4. [Bulut Dağıtımı (Render)](#bulut-dağıtımı-render)
5. [Sorun Giderme](#sorun-giderme)

---

## Sistem Gereksinimleri

### Minimum Gerekler
- **Python**: 3.8+ (3.10+ önerilir)
- **RAM**: 2 GB
- **Disk**: 500 MB boş alan
- **İşletim Sistemi**: Windows, macOS, Linux
- **Internet**: İlk kurulum sırasında (pip paketleri için)

### Yazılım Bağımlılıkları
Tüm bağımlılıklar `requirements.txt` dosyasında listelenmiştir:
- Flask 3.1.2
- SQLAlchemy ORM
- Pandas (Excel raporları)
- openpyxl (Excel format)
- Gunicorn (Üretim sunucusu)

---

## Kurulum Adımları

### **Seçenek 1: Git Klonu (Önerilen)**

En kolay ve yönetimi en uygun yöntem:

```bash
# 1. Proje dizinine gideceğiniz klasörü açın
cd C:\Users\YourUsername\Desktop

# 2. Projeyi klonlayın
git clone https://github.com/fthrkn6/SSHTakip.git

# 3. Proje klasörüne girin
cd SSHTakip

# 4. Python sanal ortamı oluşturun (önerilen)
python -m venv venv

# 5. Sanal ortamı aktifleştirin
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 6. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 7. Uygulamayı başlatın
python app.py
```

**Sonuç**: Uygulama `http://localhost:5000` adresinde açılacaktır.

---

### **Seçenek 2: Manuel Klasör Kopyalama**

Diğer bilgisayarlara USB veya ağ paylaşımı ile:

```bash
# 1. Dosyaları hedef klasöre kopyalayın
# C:\SSH_Takip gibi

# 2. Komut satırını açın ve klasöre gideyin
cd C:\SSH_Takip

# 3. Sanal ortam oluşturun
python -m venv venv

# 4. Sanal ortamı aktifleştirin
venv\Scripts\activate

# 5. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 6. Uygulamayı başlatın
python app.py
```

---

### **Seçenek 3: Tek Tıkla Başlatma (Windows)**

`RUN_SSH_TAKIP.bat` dosyası kullanarak:

```batch
@echo off
cd /d C:\SSH_Takip
if not exist venv (
    echo Sanal ortam olusturuluyor...
    python -m venv venv
)
call venv\Scripts\activate
echo Bagimliliklar yükleniyor...
pip install -r requirements.txt >nul 2>&1
echo.
echo ===================================
echo SSH Takip Sistemi baslatiliyor...
echo Tarayici otomatik acilacak: http://localhost:5000
echo ===================================
echo.
start http://localhost:5000
python app.py
pause
```

Bu dosyayı proje klasörüne kaydedin ve çift tıklayarak çalıştırın.

---

## Yerel Ağda Kullanım

### Aynı Ağdaki Farklı Bilgisayarlardan Erişim

Sunucuyu çalıştıran bilgisayarın IP adresini bulun:

**Windows:**
```bash
ipconfig
```
Çıktıda IPv4 Address (örn: 192.168.1.100) araştırın.

**Diğer bilgisayarlardan erişim:**

Başka bir bilgisayarda web tarayıcı açın ve şu adresi yazın:
```
http://192.168.1.100:5000
```

### Erişim Sorunları Giderme

1. **Güvenlik Duvarı**: Windows Güvenlik Duvarı port 5000'i engelliyorsa:
   - Başlat → Güvenlik Duvarı → İzin verilen uygulamalar
   - Python uygulamasını ağ erişimi için izin verin

2. **Ağ Bağlantısı**: İki bilgisayarın aynı WiFi/Ethernet ağında olduğundan emin olun

3. **IP Değişimi**: IP dinamik ise, `ipconfig` komutu ile yeni adresi kontrol edin

---

## Bulut Dağıtımı (Render)

### Render.com'da Canlı Dağıtım

Tüm dünyadan erişim için:

**URL**: https://bozankaya-ssh-takip.onrender.com

### İlk Dağıtım

1. GitHub'a push yapın (otomatikle senkronize olur)
2. Render Dashboard'a gidin
3. "Manual Deploy" → "Deploy latest commit"
4. 5-10 dakika bekleyin
5. Yukarıdaki URL'yi açın

### Kullanıcı Bilgileri

Varsayılan giriş:
- **Kullanıcı**: admin
- **Şifre**: admin123

### Önemli Notlar

- Render ücretsiz tier'da 15 dakika inaktiviteden sonra uyku moduna girer
- İlk erişim yavaş olabilir (uyandırılma gerekir)
- Veri kalıcı değildir (Render ücretsiz planında)
- Üretim kullanımı için ücretli plan gereklidir

---

## Sorun Giderme

### "Python bulunamadı" Hatası

Python yüklü olmadığı anlamına gelir:
- https://www.python.org adresinden Python 3.10+ yükleyin
- Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin

### "Port 5000 kullanımda" Hatası

```bash
# Kullanılan procesi bulun (Windows)
netstat -ano | findstr :5000

# PID'yi not edin, sonra işlemi sonlandırın
taskkill /PID [PID_NUMBER] /F

# Veya farklı bir port kullanın
set FLASK_PORT=5001
python app.py
```

### Bağımlılık Hatası

```bash
# Sanal ortamı yeniden oluşturun
deactivate
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Veritabanı Hatası

```bash
# Eski veritabanını silin
del ssh_takip_bozankaya.db

# Uygulamayı yeniden başlatın
python app.py
```

Uygulama otomatik olarak temiz bir veritabanı oluşturacaktır.

---

## Sık Sorulan Sorular (SSS)

### S: Başka bilgisayardan kopyalanan veriler korunur mu?

C: Evet, SQLite veritabanı (`ssh_takip_bozankaya.db`) projeye dahil edilmiştir. Verileri korumak için dosyayı düzenli olarak yedekleyin.

### S: Aynı anda birden fazla kişi kullanabilir mi?

C: Evet, hem yerel ağda hem bulutta. Her kişi web tarayıcısından aynı adresi açabilir. SQLAlchemy ORM çoklu kullanıcı erişimini destekler.

### S: Veri güvenliğini nasıl sağlarım?

C: 
- Admin şifresini değiştirin (Profil → Şifre Değiştir)
- Güvenlik duvarı kurallarını ayarlayın
- Düzenli yedekleme alın

### S: USB'den çalıştırabilir miyim?

C: Evet, tüm dosyaları USB'ye kopyalayın. Hedef bilgisayarda Python kurulu olması gerekir.

### S: Kendi sunucuma dağıtabilir miyim?

C: Evet, Gunicorn veya Nginx ile. DEPLOYMENT_GUIDE.md dosyasını kontrol edin.

---

## Hızlı Başlangıç

### En Hızlı Seçenek (5 dakika)

```bash
git clone https://github.com/fthrkn6/SSHTakip.git
cd SSHTakip
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Tarayıcı: http://localhost:5000

Giriş: admin / admin123

---

## İletişim ve Destek

Sorun veya öneriniz varsa:
- GitHub Issues: https://github.com/fthrkn6/SSHTakip/issues
- Proje Sahibi: fthrkn6

---

**Son Güncelleme**: Şubat 2026
**Sürüm**: 3.0 - Yerel Ağ & Bulut Dağıtımı
