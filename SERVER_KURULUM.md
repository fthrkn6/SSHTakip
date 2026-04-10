# SSH Takip v2.1 - Server Kurulum Rehberi

## Hızlı Kurulum (Windows Server)

### 1. Gereksinimler
- **Python 3.11+** (3.14 de çalışır)
- **Git** (opsiyonel, dosya kopyalama ile de olur)
- **Windows 10/11 veya Windows Server 2019+**

---

### 2. Projeyi Server'a Kopyala

**Seçenek A: Git ile (önerilir)**
```powershell
cd C:\
git clone <repo-url> bozankaya_ssh_takip
cd bozankaya_ssh_takip
git checkout SSHv2.1
```

**Seçenek B: USB/Dosya kopyalama**
```
Tüm proje klasörünü server'a kopyala:
  bozankaya_ssh_takip\  (ana dizin)
  ├── app.py
  ├── data\             (Excel verileri - ÖNEMLİ!)
  ├── instance\         (SQLite DB - ÖNEMLİ!)
  ├── templates\
  ├── static\
  ├── routes\
  ├── utils\
  ├── logs\
  ├── requirements.txt
  └── .env
```

> **ÖNEMLİ:** `instance\ssh_takip_bozankaya.db` ve `data\` klasörünü mutlaka kopyala. Tüm veriler bunlarda.

---

### 3. Python Kur

1. https://www.python.org/downloads/ adresinden Python 3.11+ indir
2. **"Add Python to PATH"** kutusunu işaretle
3. Kur
4. Kontrol:
```powershell
python --version
```

---

### 4. Virtual Environment ve Bağımlılıkları Kur

```powershell
cd C:\bozankaya_ssh_takip

# Virtual environment oluştur
python -m venv venv

# Aktifleştir
.\venv\Scripts\Activate.ps1

# Bağımlılıkları kur
pip install -r requirements.txt
```

> **Not:** `pip install` hata verirse şunu dene:
> ```powershell
> pip install --upgrade pip
> pip install -r requirements.txt
> ```

---

### 5. .env Dosyasını Ayarla

`.env` dosyasını düzenle:

```ini
# GÜVENLİK: Yeni SECRET_KEY üret
SECRET_KEY=buraya-yeni-uzun-rastgele-key-yaz

# Production modda çalıştır
FLASK_ENV=production

# SQLite (varsayılan, değiştirme)
DATABASE_URL=sqlite:///ssh_takip_bozankaya.db

# IP WHITELIST - Sadece bu IP'ler erişebilir
# Boş = herkes erişir, doldurursan sadece listedekiler erişir
ALLOWED_IPS=127.0.0.1,SENİN_IP_ADRESİN
```

**Yeni SECRET_KEY üretmek için:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### 6. Uygulamayı Başlat

**Basit başlatma (test için):**
```powershell
cd C:\bozankaya_ssh_takip
.\venv\Scripts\Activate.ps1
python app.py
```
→ http://localhost:5000 adresinde açılır

**Production başlatma (önerilen):**
```powershell
cd C:\bozankaya_ssh_takip
.\venv\Scripts\Activate.ps1
pip install waitress
python -m waitress --host=0.0.0.0 --port=5000 --threads=4 "app:create_app()"
```

---

### 7. Windows Servisi Olarak Çalıştır (Opsiyonel)

Bilgisayar açıldığında otomatik başlaması için:

**Seçenek A: Task Scheduler**
1. `Win + R` → `taskschd.msc`
2. "Create Basic Task" → İsim: `SSH_Takip`
3. Trigger: "When the computer starts"
4. Action: "Start a program"
   - Program: `C:\bozankaya_ssh_takip\venv\Scripts\python.exe`
   - Arguments: `-m waitress --host=0.0.0.0 --port=5000 --threads=4 "app:create_app()"`
   - Start in: `C:\bozankaya_ssh_takip`
5. "Run whether user is logged on or not" seçeneğini işaretle

**Seçenek B: start_server.bat oluştur**
```bat
@echo off
cd /d C:\bozankaya_ssh_takip
call venv\Scripts\activate.bat
python -m waitress --host=0.0.0.0 --port=5000 --threads=4 "app:create_app()"
```

---

### 8. Ağ Erişimi Ayarla

Server'a başka bilgisayarlardan erişmek için:

**Windows Firewall kuralı ekle:**
```powershell
# Yönetici PowerShell'de çalıştır
New-NetFirewallRule -DisplayName "SSH Takip Web" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

**Erişim:** `http://SERVER_IP:5000`

---

## Güvenlik Ayarları

### IP Whitelist (Uygulandı)

`.env` dosyasında `ALLOWED_IPS` ayarı ile sadece belirlenen IP'ler erişebilir:

```ini
# Tek IP
ALLOWED_IPS=192.168.1.100

# Birden fazla IP
ALLOWED_IPS=192.168.1.100,192.168.1.101,10.0.0.50

# Tüm alt ağ (192.168.1.*)
ALLOWED_IPS=192.168.1.0/24

# Karma
ALLOWED_IPS=127.0.0.1,192.168.1.0/24,10.0.0.50
```

> **Kendi IP'ni bulmak için:** `ipconfig` komutu çalıştır, IPv4 adresine bak.

### Ek Güvenlik Önlemleri

1. **Login sistemi zaten var** - Kullanıcı adı/şifre ile giriş
2. **Rate limiting** - Brute-force saldırılarına karşı koruma
3. **CSRF protection** - Form güvenliği
4. **Session timeout** - 1 saat inaktivitede oturum kapanır
5. **IP Whitelist** - Sadece izinli IP'ler erişebilir

---

## Sorun Giderme

### "ModuleNotFoundError" hatası
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Port 5000 kullanımda
```powershell
# Portu kimin kullandığını bul
netstat -ano | findstr :5000
# Farklı port kullan
python -m waitress --host=0.0.0.0 --port=8080 --threads=4 "app:create_app()"
```

### Veritabanı hatası
```powershell
# DB dosyasının var olduğundan emin ol
Test-Path instance\ssh_takip_bozankaya.db
```

### IP engellendi hatası
`.env` dosyasında `ALLOWED_IPS` satırını kendi IP'ni ekleyerek güncelle, uygulamayı yeniden başlat.

---

## Dosya Yapısı (Önemli)

```
bozankaya_ssh_takip\
├── app.py                  ← Ana uygulama
├── .env                    ← Ayarlar (SECRET_KEY, ALLOWED_IPS)
├── requirements.txt        ← Python bağımlılıkları
├── instance\
│   └── ssh_takip_bozankaya.db  ← Veritabanı (TÜM VERİLER)
├── data\
│   ├── belgrad\            ← Proje Excel dosyaları
│   ├── kayseri\
│   ├── timisoara\
│   └── ...
├── logs\                   ← Log dosyaları (otomatik oluşur)
├── routes\                 ← Sayfa route'ları
├── utils\                  ← Yardımcı fonksiyonlar
├── templates\              ← HTML şablonları
└── static\                 ← CSS, JS dosyaları
```

---

## Geri Dönüş (Rollback)

SSHv2.1 tag'ine geri dönmek için:
```powershell
git checkout SSHv2.1
```

Önceki sürüme dönmek için:
```powershell
git log --oneline
git checkout <commit-hash>
```
