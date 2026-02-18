# HBR Sistemi Kurulum & Test Kontrol Listesi

## ✅ Sistem Kontrol Listesi

### 1. Dosyalar Kontrol

- [x] **app.py**
  - [x] HBR oluşturma kodu eklendi (~140 satır, lines 689-832)
  - [x] `/hbr-listesi` route eklendi (lines 837-891)
  - [x] `/hbr-listesi/sil/<filename>` route eklendi (lines 893-918)
  - [x] `/hbr-download/<filename>` route eklendi (lines 920-945)
  - [x] Python syntax test geçti (py_compile ok)

- [x] **templates/yeni_ariza_bildir.html**
  - [x] HBR checkbox bölümü eklendi (lines 603-638)
  - [x] Form enctype="multipart/form-data" kontrol edildi
  - [x] JavaScript validasyon ve preview kodu eklendi

- [x] **templates/hbr_listesi.html**
  - [x] YENİ template oluşturuldu
  - [x] İstatistik kartları
  - [x] Dosya tablosu
  - [x] İndir/Aç/Sil butonları
  - [x] JavaScript deleteHBR fonksiyonu

- [x] **templates/ariza_listesi.html**
  - [x] HBR linki bölümü eklendi (lines 96-110)

### 2. Flask Route'ları

- [x] `/hbr-listesi` - GET - Dosya listesi
- [x] `/hbr-download/<filename>` - GET - Dosya indir
- [x] `/hbr-listesi/sil/<filename>` - POST - Dosya sil
- [x] Tüm route'larda `@login_required` kontrol

### 3. Kütüphaneler

- [x] openpyxl (3.1.5) - Kurulu
- [x] Pillow (12.0.0) - Kurulu
- [x] Flask (3.1.2) - Kurulu
- [x] Werkzeug (3.1.3) - Kurulu

### 4. Güvenlik

- [x] Path traversal koruması
- [x] Dosya adı validasyonu (BOZ-NCR- pattern)
- [x] werkzeug.utils.secure_filename() kullanımı
- [x] Login gerekmesi (@login_required)
- [x] CSRF koruması (Flask-WTF)
- [x] Resim dosya tipi validasyonu (frontend)
- [x] Dosya boyutu limiti (5MB frontend, 50MB app)

### 5. Excel Entegrasyonu

- [x] Template dosyası yükleme
- [x] Hücrelere veri yazma (15+ hücre)
- [x] Resim embed etme (PIL)
- [x] Otomatik boyutlandırma (100x100px)
- [x] Tarih formatı (DD.MM.YYYY)
- [x] NCR numaralandırması (BOZ-NCR-001, vb.)

### 6. Dosya Yönetimi

- [x] Klasör oluşturma (os.makedirs)
- [x] Temp dosya kullanımı (atomic write)
- [x] Dosya silme
- [x] Dosya indirme
- [x] Dosya listeleme

### 7. Veri Akışı

- [x] Form verilerine erişim
- [x] veriler.xlsx'den müşteri kodu okuması
- [x] Kullanıcı bilgisi (current_user.username)
- [x] Dosya yükleme işleme (request.files)
- [x] Form validation

---

## 🧪 Test Adımları

### Ön Koşullar
- [ ] Flask uygulaması çalışıyor (`python app.py`)
- [ ] Veritabanı kurulu
- [ ] Admin kullanıcı oluşturuldu
- [ ] `data/belgrad/` klasörü var
- [ ] `FR_010_R06_SSH HBR.xlsx` yerleştirildi

### Test 1: HBR Sayfasına Erişim
```
1. Browser'da http://localhost:5000/hbr-listesi açılır
2. Beklenen: Boş liste ya da mevcut dosyalar gösterilir
3. İstatistik kartları yapılır
```
**Sonuç**: ☐ Geçti ☐ Başarısız

### Test 2: Arıza Bildir Formu
```
1. http://localhost:5000/yeni-ariza-bildir açılır
2. Form alanları görülür
3. "HBR Oluştur" checkbox görülür
4. Fotoğraf alanı başlangıçta gizli (checkbox'tan sonra görünür)
```
**Sonuç**: ☐ Geçti ☐ Başarısız

### Test 3: Checkbox Davranışı
```
1. HBR checkbox'ı tıkla
2. Beklenen: Fotoğraf input bölümü görünür
3. Checkbox tekrar tıkla
4. Beklenen: Fotoğraf input bölümü gizlenir
```
**Sonuç**: ☐ Geçti ☐ Başarısız

### Test 4: Dosya Yükleme Validasyonu
```
1. Test-resim.txt dosyası seç (geçersiz tip)
2. Beklenen: JavaScript warning "Sadece resim dosyaları"
3. Geçerli JPG/PNG dosyası seç
4. Beklenen: Dosya adı ve boyutu gösterilir
```
**Sonuç**: ☐ Geçti ☐ Başarısız

### Test 5: HBR Oluşturma
```
1. Arıza form'unu doldur:
   - Malzeme No: MOTOR-001
   - Malzeme Adı: Ana Motor
   - KM: 15000
   - Tedarikçi: Siemens
   - Arıza Tarihi: 15.01.2024
   - Arıza Tanımı: Motor arızası
   - Araç Modülü: Tren Modülü 1
   - Parça Seri No: SN-2024-001
   - Arıza Sınıfı: A
   - Arıza Tipi: İlk defa
2. HBR checkbox işaretle
3. Geçerli resim dosyası seç
4. "Kaydet" tıkla
5. Beklenen: 
   - Success flash: "✅ HBR başarıyla oluşturuldu: BOZ-NCR-001"
   - Form yenilenir
```
**Sonuç**: ☐ Geçti ☐ Başarısız

### Test 6: HBR Dosyası Oluşturma Kontrolü
```
1. File explorer'da logs/belgrad/HBR/ açılır
2. Beklenen: BOZ-NCR-001_YYYYMMDDhhmmss.xlsx dosyası görülür
3. Dosya boyutu: 50KB - 500KB arasında (resime göre)
4. Dosya tarihi: Güncel (test zamanı)
```
**Sonuç**: ☐ Geçti ☐ Başarısız

### Test 7: Excel Dosyası İçeriği
```
1. BOZ-NCR-001_....xlsx dosyasını Excel'de aç
2. Kontrol et:
   ☐ A6 = MOTOR-001
   ☐ D6 = Ana Motor
   ☐ E6 = 15.01.2024 (rapor tarihi)
   ☐ G6 = 15.01.2024 (arıza tarihi)
   ☐ I6 = BOZ-NCR-001
   ☐ G7 = 15000
   ☐ J7 = Siemens
   ☐ E8 = BEL25 (veya verilen proje kodu)
   ☐ F8 = ✓ (Bozankaya kullanıcısıysa)
   ☐ G9 = ✓ (Arıza Sınıfı A)
   ☐ H9 = ✓ (Arıza Tipi - İlk defa)
   ☐ B17 = Motor arızası
   ☐ D19 = Tren Modülü 1
   ☐ G19 = SN-2024-001
   ☐ B20 = Resim görülür (100x100px)
   ☐ B22 = Kullanıcı adı
```
**Sonuç**: ☐ Geçti ☐ Başarısız

### Test 8: HBR Listesi Sayfası
```
1. http://localhost:5000/hbr-listesi açılır
2. Beklenen:
   ☐ İstatistik kartları (1 dosya, X MB, tarih)
   ☐ Tablo oluşturuldu
   ☐ BOZ-NCR-001_... listelendi
   ☐ Dosya tarihi gösterilir
   ☐ Dosya boyutu gösterilir
   ☐ İndir, Aç, Sil butonları var
```
**Sonuç**: ☐ Geçti ☐ Başarısız

### Test 9: HBR İndirme
```
1. HBR Listesi sayfasından İndir butonuna tıkla
2. Beklenen: Dosya indirilir
3. Indirilen dosya: BOZ-NCR-001_....xlsx
4. İndirilen dosya içeriği kontrol edilir
```
**Sonuç**: ☐ Geçti ☐ Başarısız

### Test 10: HBR Açma (View)
```
1. HBR Listesi sayfasından Aç butonuna tıkla
2. Beklenen: Yeni tab'ta Excel dosyası açılır VEYA indir sorusu
3. Dosya içeriği doğru
```
**Sonuç**: ☐ Geçti ☐ Başarısız

### Test 11: HBR Silme
```
1. HBR Listesi sayfasında Sil butonuna tıkla
2. Onay popup'ı çıkar
3. OK tıkla
4. Beklenen: Dosya silinir, sayfa yenilenir, statistik güncellenir
5. File explorer'da dosya yok kontrol edilir
```
**Sonuç**: ☐ Geçti ☐ Başarısız

### Test 12: Çoklu HBR Oluşturma
```
1. Test 5-6 adımlarını tekrarla (2. ve 3. HBR için)
2. Beklenen:
   ☐ BOZ-NCR-002_... oluşturulur
   ☐ BOZ-NCR-003_... oluşturulur
3. HBR Listesi'nde üç dosya listelenir
4. İstatistikler güncellenir (3 dosya, toplam boyut, son tarih)
```
**Sonuç**: ☐ Geçti ☐ Başarısız

### Test 13: Navigasyon Bağlantıları
```
1. Arıza Listesi sayfasına git
2. "HBR Listesini Aç" linki görülür
3. Linke tıkla
4. Beklenen: HBR Listesi sayfasına yönlendirilir
```
**Sonuç**: ☐ Geçti ☐ Başarısız

### Test 14: Hata Durumları
```
1. GET /hbr-download/INVALID.xlsx
2. Beklenen: 404 veya hata mesajı
3. POST /hbr-listesi/sil/../../important_file.xlsx
4. Beklenen: Güvenlik hatası, dosya silinmez
```
**Sonuç**: ☐ Geçti ☐ Başarısız

### Test 15: Özel Karakterler
```
1. Form'da Türkçe karakterler test et:
   - Arıza Tanımı: "Ür Vida Takısı Çıkmış"
   - Araç Modülü: "İçişleri Modülü"
2. HBR oluştur
3. Beklenen: Karakterler Excel'de doğru gösterilir
```
**Sonuç**: ☐ Geçti ☐ Başarısız

---

## 📋 Kurulum Sonrası Kontrol Listesi

### 1. Yapılandırma
- [ ] `data/belgrad/FR_010_R06_SSH HBR.xlsx` yerleştirildi
- [ ] `logs/belgrad/` klasörü yazılabilir
- [ ] Sistem zaman dilimi doğru (tarih timestamp)

### 2. Dosya İzinleri
- [ ] `/app.py` okunabilir
- [ ] `/templates/` klasörü okunabilir
- [ ] `/logs/` klasörü yazılabilir
- [ ] `/data/` klasörü okunabilir

### 3. Veritabanı
- [ ] User tablosu var
- [ ] Failure tablosu var
- [ ] Admin kullanıcı oluşturuldu
- [ ] Test kullanıcıları oluşturuldu

### 4. Flask Ayarları
- [ ] SECRET_KEY tanımlandı
- [ ] Upload klasörü tanımlandı
- [ ] Max content length 50MB (ayarlandı)

### 5. Bağımlılıklar
- [ ] openpyxl kurulu
- [ ] Pillow kurulu
- [ ] Flask kurulu
- [ ] requirements.txt güncellendi (isteğe bağlı)

---

## 🚀 Canlı Sunucuya Geçis

1. [ ] Tüm testler geçti
2. [ ] Documantasyon güncellendi
3. [ ] Backup alındı (eski app.py, templates)
4. [ ] Staging ortamında test edildi
5. [ ] Production'a deploy edildi
6. [ ] Kullanıcılar bilgilendirildi
7. [ ] Eğitim yapıldı (gerekirse)

---

## 📊 Özet

| İçin | Durum | Notlar |
|------|-------|--------|
| Code Review | ✅ | app.py syntax ok, templates ok |
| Security | ✅ | Path safety, auth checks |
| Database | ⏳ | Model changes: none |
| Testing | ⏳ | Manual testing needed |
| Documentation | ✅ | 2 dosya oluşturuldu |
| Deployment | ⏳ | Ready when tests pass |

---

## 🎓 Kullanıcı Eğitim

- [ ] Arıza bildirme (HBR checkbox dahil)
- [ ] Fotoğraf yükleme
- [ ] HBR Listesi görüntüleme
- [ ] Dosya indirme/silme
- [ ] Sorun giderme ipuçları

---

**Hazırlayan**: AI Pilot  
**Tarih**: 2024  
**Versiyon**: 1.0  
**Durum**: HAZIR TEST İÇİN
