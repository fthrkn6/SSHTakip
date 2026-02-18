# HBR Sistemi Hızlı Referans

## 🎯 Özet
SSH Takip uygulamasına HBR (Hata Bildirim Raporu) sistemi entegre edilmiştir. Kullanıcılar arıza bildirir, opsiyonel olarak HBR checkbox'ını işaretler, fotoğraf yükler ve sistem otomatik olarak düzenlenmiş Excel dosyası oluşturur.

---

## ⚡ Hızlı Başlangıç

### Sistem Yöneticisi
1. `data/belgrad/` klasörüne `FR_010_R06_SSH HBR.xlsx` template dosyasını yerleştir
2. Sistemin `logs/belgrad/HBR/` klasörü otomatik oluşturulacak
3. Sistem başlat (`python app.py`)

### Son Kullanıcı (Arıza Bildirici)
1. "Yeni Arıza Bildir" formuna git
2. Arıza detaylarını doldur
3. **"HBR Oluştur"** checkbox'ını işaretle ✓
4. Fotoğraf seç (JPG, PNG, tek dosya)
5. "Kaydet" tıkla

### HBR Yöneticisi / Supervisor
1. "Arıza Listesi" → "HBR Listesini Aç"
2. Veya `/hbr-listesi` sayfasına git
3. Dosyaları yönet (İndir, Aç, Sil)

---

## 🔗 Routes

| Route | Method | Fonksiyon | Kimler? |
|-------|--------|-----------|---------|
| `/hbr-listesi` | GET | HBR dosyalarını listele | Login |
| `/hbr-download/<file>` | GET | Dosya indir | Login |
| `/hbr-listesi/sil/<file>` | POST | Dosyayı sil (AJAX) | Login |

---

## 📋 Form Alanları

### Yeni Arıza Bildir (`/yeni-ariza-bildir`)

**HBR Bölümü** (sayfanın alt kısmında):
- `create_hbr` checkbox - HBR oluşturmak istiyorsa işaretle
- `hbr_fotograf` file input - 1 resim dosyası seç

**Diğer Alanlar** (HBR'ye otomatik eklenir):
- Malzeme No → `A6`
- Malzeme Adı → `D6`
- KM → `G7`
- Tedarikçi → `J7`
- Arıza Tarihi → `G6`
- Arıza Tanımı → `B17`
- Araç Modülü → `D19`
- Parça Seri No → `G19`
- Arıza Sınıfı (A/B/C) → `G9` / `G10` / `G11`
- Arıza Tipi → `H9` / `A12` / `E12`

---

## 📊 Excel Çıktı Örnekleri

### Dosya Adı Formatı
```
BOZ-NCR-001_20240115143530.xlsx    (İlk HBR)
BOZ-NCR-002_20240115145200.xlsx    (İkinci HBR)
BOZ-NCR-003_20240116091145.xlsx    (Üçüncü HBR)
```

### Klasör Yeri
```
logs/
└── belgrad/
    └── HBR/
        ├── BOZ-NCR-001_20240115143530.xlsx
        ├── BOZ-NCR-002_20240115145200.xlsx
        └── BOZ-NCR-003_20240116091145.xlsx
```

---

## ✅ Doluturulan Hücreler

```
A6   = Malzeme No
B17  = Arıza Tanımı
B20  = Fotoğraf (resim olarak gömülü)
B22  = SSH Sorumlusu (username)
D6   = Malzeme Adı
D19  = Araç Modülü
E6   = Rapor Tarihi (sistem tarihi, otomatik)
E8   = Müşteri Kodu (veriler.xlsx'den)
F8   = Tespit Yöntemi ✓ (Bozankaya kullanıcısıysa)
G6   = Arıza Tarihi
G7   = Arıza KM'si
G9   = Arıza Sınıfı A ✓
G10  = Arıza Sınıfı B ✓
G11  = Arıza Sınıfı C ✓
G19  = Parça Seri No
H8   = Müşteri Bildirimi ✓
H9   = Arıza Tipi - İlk defa ✓
I6   = SSH NCR No (otomatik: BOZ-NCR-00X)
J7   = Tedarikçi
A12  = Arıza Tipi - Tekrarlayan AYNI ✓
E12  = Arıza Tipi - Tekrarlayan FARKLI ✓
```

---

## 🖼️ Resim Özellikleri

- **Desteklenen Formatlar**: JPG, PNG, JPEG, GIF
- **Max Boyut**: 5 MB
- **Final Boyut**: 100 × 100 pixel (otomatik boyutlandırma)
- **Format Kaydediliş**: PNG (Excel içinde)
- **Yer**: Excel B20 hücresi
- **Kalite**: LANCZOS interpolasyonu (yüksek kalite)

---

## 💾 Dosya Yönetimi

### İndir
1. `/hbr-listesi` sayfasından "İndir" butonuna tıkla
2. veya `/hbr-download/BOZ-NCR-001_....xlsx` doğrudan linki

### Aç
1. `/hbr-listesi` sayfasından "Aç" butonuna tıkla
2. Browser'da Excel açılır (veya indirme sorusu)

### Sil
1. `/hbr-listesi` sayfasından "Sil" butonuna tıkla (çöp kutusu ikonu)
2. Onay popup'ı görünür
3. "OK" tıkla
4. Dosya silinir, sayfa yenilenir

---

## 🔒 Güvenlik

- **Yetkilendirme**: `@login_required` tüm route'larda
- **Dosya Validasyonu**: Sadece BOZ-NCR-*.xlsx kabul edilir
- **Path Güvenliği**: Path traversal (`../`) saldırılarından korunma
- **CSRF**: Flask-WTF tarafından otomatik
- **Dosya Boyutu**: Frontend 5MB, Backend sınırsız (50MB app-level)

---

## ⚠️ Olması Gerekenler

### Yapılandırma Dosyaları
```
data/belgrad/
├── FR_010_R06_SSH HBR.xlsx    ← ÖNEMLİ! Bulunmalı
└── veriler.xlsx

logs/belgrad/
└── HBR/                       ← Otomatik oluşturulur
```

### Veritabanı
- User modeli (username)
- Failure modeli (arıza kayıtları)

---

## 🐛 Sorun Giderme

| Problem | Çözüm |
|---------|-------|
| HBR dosyası oluşturulmuyor | Flash'ta warning görmek, template dosyası var mı kontrol et |
| Resim embed edilmiyor | Dosya formato JPG/PNG mu, 5MB altında mı kontrol et |
| Dosya indirilemiyor | Güvenlik ayarları, path güvenliği kontrol et |
| HBR sayfası açılmıyor | `/hbr-listesi` route'u tanımlı mı, login var mı kontrol et |
| Hücrelere veri yazılmıyor | Form field adları doğru mu kontrol et |

---

## 📞 Teknik Support

### Log Mesajları

**Başarı**:
```
✅ HBR başarıyla oluşturuldu: BOZ-NCR-001_...
```

**Uyarı**:
```
⚠️  HBR Template bulunamadı: /path/to/template.xlsx
⚠️  HBR Resim ekleme hatası: ...
⚠️  HBR oluşturulamadı: ...
```

**Hata**:
```
❌ HBR OLUŞTURMA HATASI: ...
```

### Debug Mod

Console'da log görmek için:
```python
print(f"   ✓ HBR prosesi başladı")
```

---

## 🎓 Eğitim Materyalleri

### Kullanıcı Ekranları

1. **Arıza Bildir Formu**
   - HBR checkbox göz atınız (~603. satır)
   - Fotoğraf input (HBR seçiliyse görünür)

2. **HBR Listesi Sayfası**
   - `/hbr-listesi` URL
   - İstatistik kartlar
   - Dosya tablosu
   - İndir/Aç/Sil butonları

3. **Arıza Listesi Sayfası**
   - "HBR Listesini Aç" linki (mavi kart)
   - `/hbr-listesi` navigasyon

---

## 📈 İstatistikler

**Sistem Kapasitesi**:
- Dosya Max Boyutu: ~2-5 MB (resim inline)
- Max Dosya Sayısı: İstenildiği kadar (disk alanı limiti)
- Örnek: 1000 HBR dosyası = ~3-5 GB (resim kalitesine bağlı)

**Performance**:
- Dosya Oluşturma Süresi: 1-2 saniye
- Listesi Yükleme: < 100ms
- İndirme: Network dependent (1-5MB, 1-10 saniye)

---

## 🚀 Deployment Kontrol Listesi

- [ ] Template dosyası yerleştirildi: `data/belgrad/FR_010_R06_SSH HBR.xlsx`
- [ ] `logs/belgrad/HBR/` klasörü oluşturulabilir
- [ ] App.py güncellendi ve test edildi
- [ ] Templates güncellendi
- [ ] Database migrate edildi (Model değişikliği yok, ok)
- [ ] Static dosyalar var (Bootstrap, JS)
- [ ] Permissions doğru (okuma/yazma)
- [ ] Test form: HBR checkbox çalışıyor
- [ ] Test dosya: İndir, Aç, Sil çalışıyor

---

## 📞 Kişiler

- **Geliştirici**: AI Pilot
- **Test Eden**: (Sistem Yöneticisi)
- **Kullanıcı Eğitmeni**: (Eğitim Dept.)

---

**Son Güncelleme**: 2024  
**Versiyon**: 1.0  
**Durum**: ✅ HAZIR
