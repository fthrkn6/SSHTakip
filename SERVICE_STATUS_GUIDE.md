# 🚊 Servis Durumu & Availability Analizi Sistemi

## 📋 Genel Bakış

Bu sistem, araçların (tramvayların) gerçek zamanlı servis durumlarını izleme, availability analizi yapma ve kök neden analizi (Root Cause Analysis) ile raporlama olanağı sağlar.

## ✨ Temel Özellikler

### 1. **Gerçek Zamanlı Durumu İzleme**
- Araçların anlık servis durumlarını görtüntüle
- Sistem ve alt sistem bazında takip
- Son durum değişikliğinin kaydı
- Daha önceki 50 olayın günlüğü

### 2. **Kapsamlı Availability Analizi**
Aşağıdaki dönemler için analiz:
- ✅ **Günlük**: Günün saati bazında
- ✅ **Haftalık**: Son 7 günün ortalaması
- ✅ **Aylık**: Ay bazında
- ✅ **3 Aylık (Quarterly)**: Çeyrek bazında
- ✅ **6 Aylık (Biannual)**: Altı ay ortalaması
- ✅ **Yıllık**: Yıl bazında
- ✅ **Total**: Sistem başlangıcından bu yana

Her analiz aşağıdakileri içerir:
- Availability yüzdesi (%)
- Operasyon saatleri
- Downtime saatleri
- Arıza sayısı

### 3. **Root Cause Analysis (RCA)**
- Sistem bazında kök neden kaydı
- Alt sistem detayları
- Severity seviyeleri (düşük, orta, yüksek, kritik)
- Oluş sıklığı
- Status takibi (açık, kapalı, beklemede)

### 4. **Excel Raporlama**
Sabit sol alt köşede bulunan 3 rapor butonu:

#### 📊 Kapsamlı Rapor
- Tüm araçlar için tüm dönemler analizi
- Özet sayfa
- Araç detay sayfaları
- Renk kodlaması (Yeşil: >95%, Sarı: 80-95%, Kırmızı: <80%)

#### 🔍 Root Cause Analysis Raporu
- Sistem bazında analiz
- Severity dağılımı
- Durum dağılımı
- Detaylı analiz tablosu

#### 📅 Günlük Rapor
- Seçili araç için o günün raporu
- Saat bazında detaylar
- Sistem ve alt sistem bilgisi
- Kaydeden kişi

### 5. **Otomatik Log Kaydı**
- Tüm durum değişiklikleri otomatik kaydedilir
- Klasör: `logs/availability/[tram_id].log`
- Format: `[YYYY-MM-DD HH:MM:SS] Status: X -> Y | System: Z | Duration: Nh`

### 6. **Raporlar Klasörü**
- Tüm Excel raporları: `logs/rapor_cikti/`
- Otomatik dosya adlandırması: `Kapsamli_Servis_Durumu_Raporu_YYYYMMDDhhmmss.xlsx`

## 🎯 Sticky Export Butonu

Sayfanın sol alt köşesinde **sabit olarak** bulunan 3 export butonu:

```
┌─────────────────┐
│  📊 Rapor       │  → Tüm araçlar için kapsamlı rapor
│  🔍 RCA         │  → Root Cause Analysis raporu
│  📅 Günlük      │  → Seçili araç için günlük rapor
└─────────────────┘
```

**Özellikler:**
- Sayfa kaydırılsa bile sabit kalır
- Animated giriş animasyonu
- Responsive tasarım
- Hover efektleri

## 📊 Dashboard Öğeleri

### Analytics Cards
- **Toplam Araç**: Sistemde kaydedilmiş araç sayısı
- **Operasyonel**: Şu anda çalışan araçlar
- **Bakım/Servis**: Bakımda veya serviste olan araçlar
- **Ortalama Availability**: Tüm araçların availability ortalaması

### Status Tablosu
- Araç ID ve adı
- Mevcut durum (badge ile renk kodlanmış)
- Sistem ve alt sistem
- Son değişim tarihi/saati
- Availability % (renk kodlanmış)
- Downtime saatleri
- Detay butonu

### Filtreler
- **Araç Seç**: Specific araç seçimi
- **Durum**: Operasyonel/Bakımda/Servis Dışı
- **Sistem**: Elektrik/Mekanik/HVAC/Seramik
- **Tarih Aralığı**: Başlangıç tarihi
- **Yenile**: Verileri manuel yenile

### Dönem Analizi
7 dönem için toggle butonları:
- Günlük
- Haftalık
- Aylık
- 3 Aylık
- 6 Aylık
- Yıllık
- Total

### Root Cause Özeti (Son 30 Gün)
- Sistem bazında kök neden sayısı
- Alt sistem detayları
- En sık kök nedenler

### Son Değişiklikler Günlüğü
- Scroll edilebilir liste
- 50 son olayın gösterilmesi
- Sistem ve alt sistem detayları

## 🗂️ Dosya Yapısı

```
servis_durumu_sistemi/
├── utils_service_status.py         # Availability analiz ve Excel generator
├── routes/service_status.py        # Route tanımları
├── templates/servis_durumu_enhanced.html  # Dashboard template
├── init_service_status.py          # Sistem initialization
├── test_service_status_data.py     # Test veri oluşturucu
└── logs/
    ├── availability/               # Log dosyaları (tram_id.log)
    └── rapor_cikti/               # Excel raporları
```

## 🔧 Kurulum ve Kullanım

### 1. Sistemi Initialize Et
```bash
python init_service_status.py
```

Çıktı:
```
✓ Klasör oluşturuldu: logs
✓ Klasör oluşturuldu: logs/availability
✓ Klasör oluşturuldu: logs/rapor_cikti
✓ Veritabanı tabloları başarıyla oluşturuldu
✅ Servis Durması Sistemi başarıyla initialize edildi!
```

### 2. Test Verileri Oluştur (Opsiyonel)
```bash
python test_service_status_data.py
```

Bu, sistemde kayıtlı araçlar için 30 günlük test verisi oluşturur.

### 3. Sayfaya Erişim
```
http://localhost:5000/servis/durumu
```

## 📡 API Endpoints

### Servis Durumu
```
GET /servis/durumu              # Dashboard sayfası
GET /servis/durumu/tablo        # Status tablosu (JSON)
POST /servis/durumu/log         # Durum değişikliği kaydet
```

### Raporlar
```
GET /servis/rapor/gunluk        # Günlük rapor (JSON)
GET /servis/rapor/haftalik      # Haftalık rapor (JSON)
GET /servis/rapor/aylik         # Aylık rapor (JSON)
GET /servis/rapor/3aylik        # 3 aylık rapor (JSON)
GET /servis/rapor/6aylik        # 6 aylık rapor (JSON)
GET /servis/rapor/yillik        # Yıllık rapor (JSON)
GET /servis/rapor/total         # Toplam rapor (JSON)
```

### Excel Raporları (Download)
```
GET /servis/excel/comprehensive-report  # Kapsamlı rapor
GET /servis/excel/root-cause-report     # RCA raporu
GET /servis/excel/daily-report/<tram_id> # Günlük rapor
```

### Root Cause Analysis
```
GET /servis/api/root-cause-summary/<tram_id>  # RCA özeti
POST /servis/root-cause                        # RCA oluştur
GET /servis/root-cause                         # RCA listesi
```

## 📊 Veri Modelleri

### ServiceLog
```python
{
    'id': Integer,
    'tram_id': String(50),          # Araç ID
    'log_date': DateTime,            # Log tarihi
    'previous_status': String(50),  # Önceki durum
    'new_status': String(50),       # Yeni durum
    'sistem': String(100),          # Sistem adı
    'alt_sistem': String(100),      # Alt sistem adı
    'reason': Text,                 # Değişiklik nedeni
    'duration_hours': Float,        # Süre (saat)
    'created_by': Integer (FK),     # Kaydeden kullanıcı
    'notes': Text                   # Notlar
}
```

### AvailabilityMetrics
```python
{
    'id': Integer,
    'tram_id': String(50),
    'metric_date': Date,
    'total_hours': Float,
    'operational_hours': Float,
    'downtime_hours': Float,
    'availability_percentage': Float,
    'failure_count': Integer,
    'report_period': String(50),    # daily, weekly, monthly, quarterly, biannual, yearly, total
    'sistem': String(100),          # Sistem bazında data (JSON)
    'alt_sistem': String(100),
    'created_at': DateTime
}
```

### RootCauseAnalysis
```python
{
    'id': Integer,
    'tram_id': String(50),
    'sistem': String(100),
    'alt_sistem': String(100),
    'failure_description': Text,
    'root_cause': Text,
    'contributing_factors': Text,   # JSON list
    'preventive_actions': Text,     # JSON list
    'corrective_actions': Text,     # JSON list
    'analysis_date': DateTime,
    'analyzed_by': Integer (FK),
    'severity_level': String(20),   # low, medium, high, critical
    'frequency': Integer,
    'status': String(50),           # open, closed, pending
    'notes': Text,
    'created_at': DateTime,
    'updated_at': DateTime
}
```

## 🎨 Renk Kodlaması

### Availability Yüzdesi
- 🟢 **Yeşil (>= 95%)**: Mükemmel
- 🟡 **Sarı (80% - 95%)**: İyi
- 🔴 **Kırmızı (< 80%)**: Kötü

### Durum Badges
- 🟢 **Yeşil**: Operasyonel
- 🟠 **Turuncu**: Bakımda
- 🔴 **Kırmızı**: Servis Dışı
- ⚪ **Gri**: Bilinmiyor

### Root Cause Severity
- 🟢 **Yeşil**: Düşük
- 🟡 **Sarı**: Orta
- 🟠 **Turuncu**: Yüksek
- 🔴 **Kırmızı**: Kritik

## 📈 Örnek Raporlar

### Kapsamlı Rapor Strukürü
1. **Özet Sayfası**
   - Tüm araçlar için tüm dönemler (Günlük, Haftalık, Aylık, 3M, 6M, 1Y, Total)

2. **Araç Detay Sayfaları** (Her araç için)
   - Dönem, Tarih Aralığı, Availability, Operational Saatleri, Downtime, Arıza Sayısı

### Root Cause Raporu Strukürü
1. **Özet Sayfası**
2. **Sistem Bazında Sayfa**
   - Sistem, Alt Sistem, Toplam Analiz, Açık, Kapalı, Beklemede
3. **Detaylı Analiz Sayfası**
   - Araç, Sistem, Alt Sistem, Arıza, Kök Neden, Severity, Sıklık, Status

## ⚙️ Konfigürasyon

### Log Klasörleri
- `logs/availability/`: Sistem log dosyaları
- `logs/rapor_cikti/`: Excel raporları

### Availability Hesaplaması
```
Availability % = (Operational Hours / Total Hours) * 100
```

### Downtime Sebepler
- Bakım (Planned)
- Arıza (Unplanned)
- Operasyon Dışı Nedeni
- Diğer

## 🔒 Güvenlik ve Yetkilendirme

- Login gereklidir
- Tüm işlemler kullanıcıya bağlıdır
- Audit trail (created_by, created_at)
- Role-based access (gelecek sürüm)

## 📞 Destek ve İletişim

Bu sistem Bozankaya Hafif Raylı Sistemi için geliştirilmiştir.

---

**Son Güncelleme**: 2026-02-04
**Versiyon**: 1.0
