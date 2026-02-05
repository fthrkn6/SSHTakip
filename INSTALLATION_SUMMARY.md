# 🎉 Servis Durumu Sistemi - Kurulum Tamamlandı

## ✅ Yapılan İşlemler

### 1. **Availability Analiz Motoru** ✓
- Günlük, haftalık, aylık, 3 aylık, 6 aylık, yıllık ve toplam analiz
- Sistem bazında downtime takibi
- Arıza sayısı ve durum analizi
- Otomatik metrik kaydı

**Dosya**: `utils_service_status.py`

### 2. **Root Cause Analysis Sistemi** ✓
- Sistem ve alt sistem bazında kök neden kaydı
- Severity seviyeleri (düşük, orta, yüksek, kritik)
- Oluş sıklığı ve status takibi
- Preventive ve corrective actions

**Kullanılan Modeller**:
- `ServiceLog`: Durum değişikliklerinin kaydı
- `RootCauseAnalysis`: Kök neden analizi
- `AvailabilityMetrics`: Availability metrikleri

### 3. **Excel Rapor Sistemi** ✓
Üç kapsamlı rapor:

#### 📊 **Kapsamlı Availability Raporu**
- Özet sayfası: Tüm araçlar için tüm dönemler
- Detay sayfaları: Her araç için ayrıntılı analiz
- Renk kodlaması (Yeşil: >95%, Sarı: 80-95%, Kırmızı: <80%)

#### 🔍 **Root Cause Analysis Raporu**
- Sistem bazında analiz
- Severity dağılımı
- Durum dağılımı (Açık/Kapalı/Beklemede)
- Detaylı analiz tablosu

#### 📅 **Günlük Rapor**
- Seçili araç için günlük durum
- Saat bazında detaylar
- Sistem ve alt sistem bilgisi

**Dosya**: `utils_service_status.py` - `ExcelReportGenerator` sınıfı

### 4. **Sticky Export Butonu** ✓
Sayfanın sol alt köşesinde sabit 3 rapor butonu:
- 📊 **Rapor**: Kapsamlı availability raporu
- 🔍 **RCA**: Root Cause Analysis raporu  
- 📅 **Günlük**: Seçili araç günlük raporu

**Özellikler:**
- Sayfanın her yerine kaydırıldığında da görünür
- Animated giriş animasyonu
- Responsive tasarım (mobil uyumlu)
- Hover efektleri
- Basit bir tıkla download başlar

**Dosya**: `templates/servis_durumu_enhanced.html`

### 5. **Otomatik Log Kaydı** ✓
- Klasör: `logs/availability/[tram_id].log`
- Format: `[YYYY-MM-DD HH:MM:SS] Status: X -> Y | System: Z | Duration: Nh`
- Tüm durum değişiklikleri otomatik kaydedilir

### 6. **Raporlanabilir Excel Çıkartma** ✓
- Klasör: `logs/rapor_cikti/`
- Otomatik dosya adlandırması: `[Rapor_Türü]_[Tarih_Saat].xlsx`
- Profesyonel formatlandırma (font, renkler, sınırlar)
- Kolay okunabilir tablolar

### 7. **Enhanced Dashboard** ✓
**Özellikler:**
- 📊 4 Analytics Card (Toplam/Operasyonel/Bakım/Ort. Availability)
- 🔽 Filtreleme seçenekleri
- 📋 Gerçek zamanlı status tablosu
- 📈 7 dönem analiz seçenekleri
- 🔍 Root Cause Özeti (Son 30 gün)
- 📝 Son değişikliklerin günlüğü
- 🎨 Modern, responsive tasarım
- 🔄 30 saniyede bir otomatik yenile

**Dosya**: `templates/servis_durumu_enhanced.html`

### 8. **Route Güncellemeleri** ✓
Yeni route'lar:
```
GET /servis/durumu                          # Ana dashboard
GET /servis/durumu/tablo                    # Status tablosu (JSON)
POST /servis/durumu/log                     # Durum değişikliği kaydet
GET /servis/excel/comprehensive-report     # Kapsamlı rapor
GET /servis/excel/root-cause-report        # RCA raporu
GET /servis/excel/daily-report/<tram_id>   # Günlük rapor
GET /servis/api/root-cause-summary/<tram_id> # RCA özeti (JSON)
```

**Dosya**: `routes/service_status.py`

## 📁 Oluşturulan Dosyalar

```
✓ utils_service_status.py              # Analiz ve rapor motoru (650 satır)
✓ templates/servis_durumu_enhanced.html # Dashboard template (600 satır)
✓ routes/service_status.py             # Route güncellemeleri
✓ init_service_status.py               # Sistem initialization
✓ test_service_status_data.py          # Test veri oluşturucu
✓ SERVICE_STATUS_GUIDE.md              # Kapsamlı dokümantasyon
✓ logs/                                # Log klasörü
  ├── availability/                    # Sistem log dosyaları
  └── rapor_cikti/                     # Excel raporları
```

## 🚀 Başlangıç Kılavuzu

### Adım 1: Sistemi Initialize Et
```bash
python init_service_status.py
```

Çıktı:
```
✓ Klasör oluşturuldu: logs/availability
✓ Klasör oluşturuldu: logs/rapor_cikti
✓ Veritabanı tabloları başarıyla oluşturuldu
✅ Servis Durumu Sistemi başarıyla initialize edildi!
```

### Adım 2: Test Verileri Oluştur (Opsiyonel)
```bash
python test_service_status_data.py
```

Sistem yazılı araçlar için 30 günlük örnek veri oluşturur.

### Adım 3: Uygulamayı Başlat
```bash
python app.py
```

### Adım 4: Sayfaya Erişim
```
http://localhost:5000/servis/durumu
```

## 📊 Sistemi Kullanmak

### Dashboard'da Yaptıklarınız:

1. **Araçların Durumunu İzleyin**
   - Gerçek zamanlı status tablosu
   - Sistem ve alt sistem detayları
   - Son değişim zamanları

2. **Availability Analizi Yapın**
   - 7 farklı dönem seçeneği
   - Renk kodlanmış yüzdeler
   - Grafik analizi (geliştirilecek)

3. **Root Cause Analysis İnceleyin**
   - Sistem bazında kök nedenler
   - Severity dağılımı
   - Oluş sıklıkları

4. **Raporları İndirin**
   - Sol alt sabit buton
   - 3 rapor türü
   - Professional Excel formatı

5. **Filtreleyin ve Sıralayın**
   - Araç bazında filtre
   - Durum filtresi
   - Sistem filtresi
   - Tarih filtresi

## 🎯 Sticky Export Buton

**Konumu**: Sayfanın sol alt köşesi (sabit)

**Butonlar**:
```
┌─────────────────────────────┐
│ 📊 Rapor (Yeşil)           │ → Kapsamlı Availability Raporu
│ 🔍 RCA (Turuncu)           │ → Root Cause Analysis Raporu
│ 📅 Günlük (Mavi)           │ → Seçili Araç Günlük Raporu
└─────────────────────────────┘
```

**Kullanım**:
1. Rapor türünü seçin
2. Günlük rapor için araç seçin (filtre alanından)
3. Butona tıklayın
4. Excel dosyası otomatik indirilir

## 📈 Availability Hesaplaması

```
Availability % = (Operational Hours / Total Hours) × 100

Örnek:
- Toplam Saatler: 24
- Operasyon Saatleri: 22
- Downtime Saatleri: 2
- Availability: 91.67%
```

## 🗂️ Log Dosyaları

**Konum**: `logs/availability/[tram_id].log`

**Format**:
```
[2026-02-04 14:30:15] Status: operasyonel -> bakımda | System: Elektrik | SubSystem: Pantograf | Reason: Periyodik bakım | Duration: 2.5h
[2026-02-04 16:45:20] Status: bakımda -> operasyonel | System: Elektrik | SubSystem: Pantograf | Reason: Bakım tamamlandı | Duration: 2.5h
```

## 💾 Excel Raporları

**Konum**: `logs/rapor_cikti/`

**Dosya Adlandırması**:
- `Kapsamli_Servis_Durumu_Raporu_20260204_143015.xlsx`
- `Root_Cause_Analiz_Raporu_20260204_143015.xlsx`
- `Gunluk_Durum_TRAM-001_20260204.xlsx`

## 🎨 Stil ve Tasarım

### Renk Şeması
- 🟣 **Primary**: #667eea (Mor-Mavi)
- 🟠 **Secondary**: #764ba2 (Koyu Mor)
- 🟢 **Success**: #4CAF50 (Yeşil)
- 🟠 **Warning**: #FF9800 (Turuncu)
- 🔴 **Danger**: #f44336 (Kırmızı)

### Responsive Tasarım
- Desktop: 1440px+
- Tablet: 768px - 1024px
- Mobile: < 768px

## 🔐 Güvenlik

- Login gereklidir
- Tüm işlemler kullanıcıya bağlıdır
- Audit trail (created_by, created_at, updated_at)
- Database içinde şifreli saklama

## 🎓 Eğitim Materyalleri

Kapsamlı rehber: `SERVICE_STATUS_GUIDE.md`

İçerik:
- Genel bakış
- Özellikler detayları
- API Endpoints
- Veri modelleri
- Renk kodlaması
- Raporlar yapısı

## ⚡ Performance Notları

- Dashboard 30 saniyede bir otomatik yenile
- Large raporlar için Excel library optimizasyonu
- Database indexleri (tram_id, metric_date, report_period)
- JSON storage sistem bazında analiz için

## 🔄 Gelecek Sürümler İçin (TODO)

- [ ] Grafik görselleri (Chart.js entegrasyon)
- [ ] Email raporları
- [ ] Role-based access kontrol
- [ ] Bakım takvimi entegrasyon
- [ ] SMS alert sistemi
- [ ] Mobile app
- [ ] BI dashboard (Power BI/Tableau)
- [ ] Predictive maintenance

## 📞 Desteği İletişim

Sistem Bozankaya Hafif Raylı Sistemi için geliştirilmiştir.

---

**Kurulum Tarihi**: 2026-02-04
**Versiyon**: 1.0.0
**Durum**: ✅ Üretim Hazır
