# SSH Takip Sistemi - Hızlı Başlangıç

## 🚀 30 Saniye Başlangıç (Windows)

### Seçenek 1: Tek Tıkla (En Kolay)
1. `RUN_SSH_TAKIP.bat` dosyasını **çift tıklayın**
2. Uygulama otomatik açılacak
3. Hazır!

**Erişim**: http://localhost:5000

---

### Seçenek 2: Komut Satırı
```bash
# Proje klasörüne gidin
cd C:\Users\YourName\Desktop\SSHTakip

# Başlatın
RUN_SSH_TAKIP.bat
```

---

## 🌐 Başka Bilgisayardan Erişim

### Aynı Ağda İseniz:

1. Sunucu çalıştıran bilgisayarın IP'sini bulun:
   ```bash
   ipconfig
   ```
   
   **IPv4 Address**'i not edin (örn: 192.168.1.100)

2. Başka bilgisayarda tarayıcıda açın:
   ```
   http://192.168.1.100:5000
   ```

### İnternetten İseniz:

Bulut link kullanın:
```
https://bozankaya-ssh-takip.onrender.com
```

---

## 🔑 Giriş Bilgileri

| Alan | Değer |
|------|-------|
| Kullanıcı Adı | `admin` |
| Şifre | `admin123` |

⚠️ **Önemli**: Güvenlik için şifreyi değiştirin (Profil → Şifre Değiştir)

---

## 📱 Tüm Cihazlardan Erişim

✅ Bilgisayar (Windows, Mac, Linux)
✅ Telefon (iPhone, Android)
✅ Tablet
✅ Herhangi bir web tarayıcısı

---

## 💾 Yedekleme

Veritabanı dosyasını düzenli yedekleyin:
```
ssh_takip_bozankaya.db
```

Klasörü yedekleme alanına kopyalayın veya bulut depolamasında tutun.

---

## ⚙️ Ayarlar

### Port Değiştirme (5000'den farklı)

`RUN_SSH_TAKIP.bat` içinde bulun ve değiştirin:
```batch
python app.py --port 8080
```

### Şifre Sıfırlama

`admin123` şifresi unutuluyor sa:
1. `ssh_takip_bozankaya.db` dosyasını silin
2. Uygulamayı yeniden başlatın
3. Varsayılan şifre `admin123` olacak

---

## ❓ Sorunlar

| Sorun | Çözüm |
|-------|-------|
| Port 5000 kullanımda | Farklı port deneyebilirsiniz: `python app.py --port 8080` |
| Python bulunamadı | Python 3.8+ yükleyin: https://www.python.org |
| Ağ erişim yok | Windows Güvenlik Duvarı ayarlarını kontrol edin |
| Veritabanı hatası | `ssh_takip_bozankaya.db` dosyasını silin |

---

## 📚 Detaylı Kurulum

Adım adım rehber için [SETUP.md](SETUP.md) dosyasını okuyun.

---

**Şubat 2026 - SSH Takip v3.0**
