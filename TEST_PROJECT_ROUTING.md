# İstanbul ve Samsun Proje Yönlendirmesi Test  

## Sorun
Yeni 2 adet proje ekledim (istanbul ve samsun) ancak projeleri seçip girdiğimde belgrad projesi sayfasına gidiyor.

## Yapılan Düzeltmeler

### 1. app.py - PROJECTS Liste (✅ Düzeltildi)
- İstanbul projesi PROJECTS listesine eklendi
- Kod: `{'code': 'istanbul', 'name': 'İstanbul', 'country': 'Türkiye', 'flag': '🇹🇷'}`

### 2. login.html - Fallback Projeler (✅ Düzeltildi)  
- Fallback projeler listesine İstanbul eklendi
- Bu fallback, `/api/projects` API çağrısı başarısız olursa kullanılır
- Tüm 8 proje artık fallback'de mevcut

### 3. login.html - Form Submit Handler (✅ Düzeltildi)
- JavaScript addEventListener DOMContentLoaded'ye taşındı (timing fix)
- Auto-select logic: Eğer proje seçilmemişse, form submit sırasında ilk geçerli proje otomatik seçilir
- Debug console.log eklendi: Form submit sırasında project value'sü console'da görülebilir

### 4. app.py - Login Endpoint Logging (✅ Eklendi)
- Form project value'sü loglama eklendi
- Kullanılabilir projeler listesi loglama eklendi
- Project validation sonucu loglama eklendi
- Terminalde: `[LOGIN] Form project value: 'istanbul'` gibi output görülecek

### 5. routes/dashboard.py - Dashboard Index (✅ Eklendi)  
- Query parametresinden project override desteği eklendi
- Test için: `/dashboard?project=istanbul` çağırabileceksiniz

## Test Adımları

### Test 1: API Endpoint Kontrol
```bash
curl http://localhost:5000/api/projects
```
Beklenen sonuç: istanbul ve samsun projelerini içeren JSON listesi

### Test 2: Login İle Test
1. Sayfayı tarayıcıda açın: `http://localhost:5000/login`
2. Browser Console'u aç (F12 → Console)
3. Proje Seçin dropdown'undan İstanbul seçin
4. Console'da: `Final project value: istanbul` görmeli
5. Login bilgilerinizi girin ve login yapın
6. Terminalde: `[LOGIN] Form project value: 'istanbul'` ve `[LOGIN] Project set to: istanbul` görmeli
7. Dashboard açılmalı ve İstanbul verilerini göstermeli

### Test 3: Debug Query Param
İsterseniz doğrudan dashboard'a git:
```
http://localhost:5000/dashboard?project=istanbul
```
Bu da doğru proje verisini gösterecektir.

## Debugging

### Konsol Hataları
- Browser F12 → Console sekmesinde herhangi bir hata var mı kontrol edin
- Network sekmesinde `/api/projects` çağrısı başarılı mı kontrol edin

### Terminal Çıktısı
Flask uygulamasını terminal'de çalıştırırken:
- `[LOGIN]` ile başlayan lineleri takip edin
- Project value'sü doğru mu kontrol edin

## Verifier Kontrolü

### Veriler.xlsx Dosyaları
- ✅ `data/istanbul/Veriler.xlsx` - Var
- ✅ `data/samsun/Veriler.xlsx` - Var

### API Endpoint
- `/api/projects` endpoint'i `data/` klasöründen dinamik olarak direkt okuyur
- Klasörde Veriler.xlsx varsa, proje listesine eklenir

## Hala Sorun Varsa

Lütfen şunları kontrol edin:
1. **Flask uygulmasını yeniden başlatın** - Kod değişiklikleri yüklenmek için
2. **Cache temizle** - Tarayıcı F12 → Storage → Cookies → Delete
3. **İncognito/Private mode'da test edin** - Cache sorunlarını ortadan kaldırmak için
4. **Terminal çıktısını paylaş** - `[LOGIN]` loglama çıktısını kontrol etmek için

## İlgili Dosyalar
- `app.py` - PROJECTS liste (satır 57-75)
- `app.py` - Login endpoint (satır 352-369)
- `templates/login.html` - Form ve JavaScript (satır 313-432)
- `routes/dashboard.py` - Dashboard index (satır 453-460)
- `data/istanbul/Veriler.xlsx` - İstanbul veri dosyası
- `data/samsun/Veriler.xlsx` - Samsun veri dosyası
