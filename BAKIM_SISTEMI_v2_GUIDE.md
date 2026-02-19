# Bakım Planlama Sistemi v2.0 - Implementasyon Guide

## 📋 Genel Bakış

Bakım planlama sistemi aşağıdaki özellikleri sağlar:

1. **Bakım Kartı Upload & İmza**: Bakım tamamlandığında dosya ve imza kaydı
2. **Transpoze Bakım Tablosu**: Satırda araçlar, sütunda bakım seviyeleri
3. **Dinamik Renklendirme**: Bakıma ne kadar yakın olduğuna göre hüvre rengi
4. **Belgrad-Bakım Excel İçeriği**: Her bakım seviyesinin detaylı maddelerini görüntüleme

---

## 🔧 Teknik Mimarisi

### Backend (app.py)

**Yeni API Endpoints:**

1. **`POST /api/bakim-upload`**
   - Bakım kartı dosyası upload eder
   - İmza göğüne kaydeder (Base64 PNG)
   - Dosyalar: `logs/belgrad/Bakım/` klasörüne kaydedilir
   - Dosya adı: `YYYYMMDD_HHMMSS_TramID_Level_filename`
   - İmza dosyası: `YYYYMMDD_HHMMSS_TramID_Level_signature.png`

2. **`GET /api/bakim-excel-sheets`**
   - Belgrad-Bakım.xlsx'deki tüm sheet'leri listeler
   - Response: `{sheets: [...]}`

3. **`GET /api/bakim-sheet-items/<sheet_name>`**
   - Belgrad-Bakım.xlsx'deki belirli sheet'in maddeleri döner
   - Response: `{sheet: "6K", items: [...], count: N}`

4. **`GET /api/bakim-tablosu-transpose`**
   - Transpoze bakım tablosunu döner
   - Satırda araçlar, sütunda bakımlar
   - Dolar KM ve durum bilgisi ile birlikte
   - Response: 
     ```json
     {
       "maintenance_levels": ["6K", "18K", "24K", ...],
       "tramps": [
         {
           "tram_id": "TRN-1234",
           "current_km": 45000,
           "maintenance_status": {
             "6K": {"status": "warning", "progress": 82, "km_left": 1200, ...},
             "18K": {"status": "normal", "progress": 25, "km_left": 12000, ...}
           }
         }
       ]
     }
     ```

### Frontend (templates/bakim_planlari.html)

**Modal'lar:**

1. **Bakım Kartı Upload Modal** (`#bakim_upload_modal`)
   - Dosya seçme
   - İmza canvas (opsiyonel)
   - İmzayı temizle/indir butonları

**Tab 2 Değişiklikleri:**

- **Eski format**: KM-bazlı schedule (mevcut hala orada ama kullanılmıyor)
- **Yeni format**: Transpoze tablo (satırda araçlar, sütunda bakımlar)
- Tıklandığında: `showBakimDetails()` → Belgrad-Bakım.xlsx sheet'i açılır

**JavaScript Fonksiyonları:**

- `openBakimUploadModal(tramId, level)`: Upload modal'ı aç
- `submitBakimUpload()`: Dosya ve imzayı upload et
- `loadTransposeMaintenance()`: Transpoze tablo verisi al
- `renderTransposeTable(data)`: Tabloyu render et
- `showBakimDetails(level, tramId, progress)`: Detaylar modal'ı aç
- `initBakimSignaturePad()`: İmza canvas'ını hazırla
- `clearBakimSignature()` ve `downloadBakimSignature()`: İmza kontrol fonksiyonları

---

## 📊 Veri Akışı

```
Kullanıcı "Tamamla" Buttonu
    ↓
openBakimUploadModal(tramId, level)
    ↓
[Upload Modal Açılır]
    ↓
Kullanıcı dosya seçer + opsiyonel imza çizer
    ↓
submitBakimUpload()
    ↓
POST /api/bakim-upload
    ↓
logs/belgrad/Bakım/ klasörüne kaydedilir
    ↓
maintenanceState[tramId][level].completed = true
    ↓
localStorage'a kaydedilir
    ↓
Tablo yenilenir
```

### Transpoze Tablo:

```
GET /api/bakim-tablosu-transpose
    ↓
Equipment tablosundan araçlar ve km'ler çekilir
    ↓
maintenance.json'dan bakım seviyeleri okunur
    ↓
Her araç × her bakım için durum hesaplanır
    ↓
renderTransposeTable() ile tablo gösterilir
    ↓
Hücreye tıklandığında showBakimDetails()
    ↓
GET /api/bakim-sheet-items/<level> ile sheet açılır
```

---

## 🎨 Renk Kodlaması

Transpoze tablo'daki hücreler:

| Durum | Terim | Renk | Koşul |
|-------|-------|------|-------|
| Normal | 0-70% | 🟢 #d4edda | `km_left > level_km * 0.7` |
| Uyarı | 70-90% | 🟡 #fff3cd | `km_left > level_km * 0.1` |
| Acil | 90-100% | 🔴 #f8d7da | `km_left <= level_km * 0.1` |
| Geçmiş | <0% | ⚫ #e2e3e5 | `km_left < 0` |

---

## 📁 Dosya Yapısı

```
logs/belgrad/
├── Bakım/                    # YENİ - Bakım kartları ve imzalar
│   ├── 20260219_093000_TRN-1234_6K_bakım_kartı.pdf
│   ├── 20260219_093000_TRN-1234_6K_signature.png
│   └── ...
├── HBR/
├── ariza_listesi/
└── ...

data/belgrad/
├── Belgrad-Bakım.xlsx        # Sheet'ler: 6K, 18K, 24K, ...
├── maintenance.json          # Bakım seviyeleri ve işler
└── ...
```

---

## 🔍 Önemli Notlar

### Belgrad-Bakım.xlsx Sheet Adları

Şu anda app.py'de sheet adı olarak **6K, 18K, 24K, VS.** bekleniyor. 
Eğer farklı adlar varsa, sheet'leri kontrol et ve app.py'deki `/api/bakim-sheet-items/<sheet_name>` endpoint'inde düzelt.

**Şu anda Belgrad-Bakım.xlsx'de olması gereken sheet'ler:**
```
- 6K (6000 KM Bakımı)
- 18K (18000 KM Bakımı)
- 24K (24000 KM Bakımı)
- 36K (36000 KM Bakımı)
- 60K (60000 KM Bakımı)
- 72K (72000 KM Bakımı)
- 85K (85000 KM Bakımı)
- 100K (100000 KM Bakımı)
- 120K (120000 KM Bakımı)
- 140K (140000 KM Bakımı)
```

### Tab 2 Tab Adı

Şu anda Tab 2 adı "Bakım Planı Tablosu" ama **aslında artık eski horz-tab görünüşünü değil, yeni transpoze tabloyu gösteriyordur.**

---

## ✅ Test Adımları

1. **Bakım Planlama Sayfasını Aç**
   ```
   http://localhost:5000/bakim-planlari
   ```

2. **Tab 1 - Araç Durumu**
   - Araçların durumunu görebilmelisdin (Normal / Uyarı / Acil)
   - Bir araçın modal'ını aç (click on row)
   - "Tamamla" butonu içinde bakım seviyelerini görebilmelisin

3. **"Tamamla" Buttonu Testi**
   - Bir bakım seviyesinde "Tamamla"ya tıkla
   - Upload modal açılmalı
   - Dosya seç (herhangi bir dosya olabilir)
   - Opsiyonel: İmza çiz
   - "Yükle" buttonu
   - Başarı mesajı ve dosya `logs/belgrad/Bakım/` içinde kaydedilince yapı çalışıyor

4. **Tab 2 - Transpoze Tablo**
   - Tüm araçlar ve bakım seviyeleri görülmeli
   - Hücrelerin renkleri durama göre değişmeli
   - Hücreye tıklanıverindığinde (click cell):
     - "Bakım Detayları" modal açılmalı
     - Belgrad-Bakım.xlsx'den ilgili level'in maddeleri gösterilmeli
     - "Bakım Kartı Yükle" butonu ile upload modal açılabilmeli

---

## 🐛 Olası Sorunlar

### Problem 1: Belgrad-Bakım.xlsx Sheet Adları Uyuşmuyorsa

**Çözüm:**
1. Belgrad-Bakım.xlsx'i aç
2. Sheet adlarını kontrol et
3. `app.py` line ~1877'deki `/api/bakim-tablosu-transpose` endpoint'inde sheet adlarını güncelle:
   ```python
   maintenance_levels = sorted([k for k in maintenance_data.keys() if k not in ['70K', '140K']], ...)
   ```

### Problem 2: Transpoze Tablo Boş Görünüyorsa

**Kontrol edenler:**
1. Equipment tablosunun aktif araçları olup olmadığını kontrol et
2. Browser Console'da hata var mı kontrol et (F12)
3. `/api/bakim-tablosu-transpose` endpoint'ini test et (Postman, etc.)

### Problem 3: İmza Canvas'ında Mouse Olayları Çalışmıyorsa

**Çözüm:**
- Canvas'taki z-index sorunları olabilir
- CSS'te `#bakim_signature_canvas { cursor: crosshair; }` eklenmiş
- Ama eğer yine sorun varsa, mouse event listener'ları kontrol et

---

## 🚀 Gelecek Geliştirmeler

- [ ] İmza verifikasyonu (Sertifika tabanlı)
- [ ] Bakım Kartı PDF export (imza ile)
- [ ] Bakım tarihine göre rapor
- [ ] Araçlara göre bakım takvimi export (Excel)
- [ ] Bildirim systemi (Yaklaşan bakım)
- [ ] Bakım ekibi assignment

---

## 📝 Dosyalar Değiştirildi

- `app.py`: 4 yeni endpoint eklendi (~140 satır)
- `templates/bakim_planlari.html`: Upload modal + JavaScript (~350 satır)
- `logs/belgrad/Bakım/`: YENİ klasör oluşturuldu

---

**Tarih:** 19.02.2026  
**Sürüm:** v7.2
