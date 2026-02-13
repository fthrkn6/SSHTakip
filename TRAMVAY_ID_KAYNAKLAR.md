# Tramvay/Araç ID'lerinin Çekildiği Kaynaklar - Tam Analiz

## 📊 ÖZET
Projede tramvay araç ID'leri **6 farklı yerden** çekiliyor ve **4 farklı format** kullanılıyor.

---

## 🗺️ DETAYLI HARITA

### 1️⃣ **DASHBOARD (/dashboard)** 
**Sayfa:** Dashboard (Ana Sayfa)

#### Kaynak 1A: Equipment Veritabanı (PRIMARY)
- **Dosya:** `app.py` + `routes/dashboard.py`
- **Fonksiyon:** `def index()` (lines 241-354 in routes/dashboard.py)
- **Query:** `Equipment.query.filter_by(parent_id=None, project_code=current_project).all()`
- **Format:** `equipment.equipment_code` (string, örn: "1", "2", "K001")
- **Lookup:** 
  - `equipment.id` (integer ID)
  - `equipment.equipment_code` (human-readable)
  - `equipment.name` (display name)
- **Amaç:** Tramvay filosu durumu, status, KM

#### Kaynak 1B: Excel - Arıza Listesi (FALLBACK)
- **Dosya:** `routes/dashboard.py`
- **Fonksiyon:** `def get_failures_from_excel()` (lines 12-51)
- **Konum 1:** `logs/{project}/ariza_listesi/Ariza_Listesi_{PROJECT}.xlsx`
  - Sheet: 'Ariza Listesi'
  - Header: Row 3 (0-indexed)
- **Konum 2 (Fallback):** `data/{project}/Veriler.xlsx`
  - Sheet: 'Veriler'
  - Header: Row 0
- **Format:** Colonna sütunundan tramvay verileri çekilir
- **Amaç:** Son 5 açık arıza, arıza sınıfı istatistikleri

#### Kaynak 1C: ServiceStatus Veritabanı
- **Dosya:** `routes/dashboard.py`
- **Query:** `ServiceStatus.query.filter_by(date=today_date).all()`
- **Format:** `status_record.tram_id` (string)
- **Amaç:** Bugünün servis durumu

---

### 2️⃣ **SERVİS DURUMU (/servis/durumu)**
**Sayfa:** Servis Durumu Dashboard

#### Kaynak 2A: Equipment Veritabanı (PRIMARY)
- **Dosya:** `routes/service_status.py`
- **Fonksiyon:** `def service_status_page()` (lines 26-116)
- **Query:** `Equipment.query.filter_by(parent_id=None, project_code=current_project).all()`
- **Format:** `equipment.equipment_code`
- **Amaç:** Tüm araçlar, servis durumu

#### Kaynak 2B: ServiceStatus Veritabanı
- **Dosya:** `routes/service_status.py`
- **Query:** `ServiceStatus.query.filter_by(tram_id=equipment.equipment_code, date=today_date).first()`
- **Format:** `status_record.tram_id` (eşleştirilir equipment_code ile)
- **Amaç:** Tarih bazlı durumlar

#### Kaynak 2C: AvailabilityMetrics Veritabanı
- **Dosya:** `routes/service_status.py`
- **Query:** `AvailabilityMetrics.query.filter_by(tram_id=equipment.equipment_code)`
- **Format:** `metric.tram_id`
- **Amaç:** Availability metrikleri

---

### 3️⃣ **KPI DASHBOARD (/kpi)**
**Sayfa:** KPI Dashboard

#### Kaynak 3A: Arıza Listesi Excel (PRIMARY)
- **Dosya:** `routes/kpi.py`
- **Fonksiyon:** `def get_ariza_listesi_data()` (lines 53-99)
- **Konum 1:** `logs/{project}/ariza_listesi/Ariza_Listesi_{PROJECT}.xlsx`
  - Sheet: 'Ariza Listesi'
  - Header: Row 3
- **Konum 2 (Fallback):** `data/{project}/Veriler.xlsx`
  - Sheet: 'Veriler'
  - Header: Row 0
- **Format:** Excel sütunlarından dinamik çekilir
- **Amaç:** FRACAS ID ile arıza verileri

#### Kaynak 3B: Equipment Veritabanı
- **Dosya:** `routes/kpi.py`
- **Query:** `Equipment.query.all()[].equipment_code`
- **Format:** `equipment.equipment_code`
- **Amaç:** İstatistik hesaplaması

---

### 4️⃣ **FRACAS ANALİZİ (/fracas)**
**Sayfa:** FRACAS Analiz Sayfası

#### Kaynak 4A: Arıza Listesi Excel (PRIMARY)
- **Dosya:** `routes/fracas.py`
- **Fonksiyon:** `def load_ariza_listesi_data()` (lines 144-197)
- **Konum 1:** `logs/{project}/ariza_listesi/Ariza_Listesi_{PROJECT}.xlsx`
  - Sheet: 'Ariza Listesi'
  - Header: Row 3
  - Sütun: 'Araç Numarası Vehicle Number'
- **Konum 2 (Fallback):** `data/{project}/Veriler.xlsx`
  - Sheet: 'Veriler'
  - Header: Row 0
- **Format:** Dinamik sütun arama ("vehicle" + "number" kombina)
- **Amaç:** FRACAS ID'lerle araç numaralarını eşleştir

#### Kaynak 4B: Dynamik Excel Arama
- **Dosya:** `routes/fracas.py` lines 200+
- **COLUMN_MAPPING:** 40+ sütun eşlemesi yapılıyor
- **Amaç:** Detaylı arıza analizi

---

### 5️⃣ **YENİ ARIZA BİLDİR (/yeni-ariza-bildir)**
**Sayfa:** Yeni Arıza Formunu

#### Kaynak 5A: Veriler.xlsx - Sayfa2 (PRIMARY)
- **Dosya:** `app.py`
- **Fonksiyon:** `def yeni_ariza_bildir()` (lines 159-340)
- **Konum:** `data/{current_project}/Veriler.xlsx`
  - Sheet: 'Sayfa2' 
  - Header: Row 0
  - Sütun: Dinamik arama ('tram' + 'id' içeren sütun)
- **Format:** String int'e çevrilir: `str(int(t))`
- **Amaç:** Dropdown'da tramvay seçeneği

#### Kaynak 5B: Arıza Listesi Excel (VERIFY)
- **Dosya:** `app.py` lines 169-205
- **Konum:** `logs/{current_project}/ariza_listesi/Ariza_Listesi_{PROJECT}.xlsx`
- **Amaç:** Son FRACAS ID'yi hesapla (next ID generation)

---

### 6️⃣ **ARIZA LİSTESİ SAYFASI (/ariza-listesi-veriler)**
**Sayfa:** Arıza Listesi Tablosu ve İndirme

#### Kaynak 6A: Arıza Listesi Excel (PRIMARY)
- **Dosya:** `app.py`
- **Fonksiyon:** `def ariza_listesi_veriler()` (lines 559-667)
- **Konum 1:** `logs/{project}/ariza_listesi/Ariza_Listesi_{PROJECT}.xlsx`
  - Sheet: 'Ariza Listesi'
  - Header: Row 3
- **Konum 2 (Fallback):** `data/{project}/Veriler.xlsx`
  - Sheet: 'Veriler'
  - Header: Row 0
- **Format:** Tüm sütunlar dinamik
- **Amaç:** Tabloda tüm arıza verilerini göster

---

### 7️⃣ **BAKIM PLANLARI (/maintenance/plans)**
**Sayfa:** Bakım Planları

#### Kaynak 7A: trams.xlsx Excel
- **Dosya:** `routes/maintenance.py`
- **Fonksiyon:** `def load_trams_from_file()` (lines 11-35)
- **Konum:** `data/{project_code}/trams.xlsx`
  - Sheet: İlk sheet
  - Header: Row 0
  - Sütun: 'tram_id'
- **Format:** String direkt
- **Amaç:** Bakım planı formunda tramvay dropdown

#### Kaynak 7B: MaintenancePlan Veritabanı
- **Dosya:** `routes/maintenance.py`
- **Query:** `MaintenancePlan.query.filter_by(is_active=True)`
- **Amaç:** Bakım planları listesi

---

### 8️⃣ **ARIZA EKLE (/ariza-ekle, /is-emri-ekle, /bakim-plani-ekle)**
**Sayfalar:** Form sayfaları

#### Kaynak 8A: Veriler.xlsx - Sayfa2
- **Dosya:** `app.py` (yeni_ariza_bildir fonksiyonu ile aynı)
- **Konum:** `data/{project}/Veriler.xlsx`
- **Amaç:** Formda tramvay dropdown

---

## 📈 KAYNAKLAR İSTATİSTİKSİ

| Kaynak | Tip | Format | Dosya Yolu | Kullanılan Sayfalar |
|--------|-----|--------|-----------|-------------------|
| **Equipment DB** | Veritabanı | equipment_code | DB | Dashboard, Servis Durumu, KPI |
| **ServiceStatus DB** | Veritabanı | tram_id | DB | Dashboard, Servis Durumu |
| **Arıza Listesi** | Excel | Dinamik Sütun | `logs/{p}/ariza_listesi/` | KPI, FRACAS, Arıza Listesi, Yeni Arıza |
| **Veriler.xlsx** | Excel | tram_id sütunu | `data/{p}/Veriler.xlsx` | Yeni Arıza, Arıza Ekle, İş Emri |
| **trams.xlsx** | Excel | tram_id sütunu | `data/{p}/trams.xlsx` | Bakım Planları |
| **Maintenance.json** | JSON | Hardcoded | `data/belgrad/maintenance.json` | Bakım Planları API |

---

## 🔄 VERİ AKIŞI HARITASI

```
┌─────────────────────────────┐
│   Kullanıcı Giriş (Login)   │
│  (session['current_project'])│
└────────────┬────────────────┘
             │
    ┌────────▼────────────┐
    │  Project Selection  │
    │ (Belgrad/Kayseri)   │
    └────────┬────────────┘
             │
    ┌────────▼──────────────────────────────────────┐
    │    TÜM PAGES - Dynamic Project Selection      │
    └────┬───────┬──────────┬───────┬───────┬──────┘
         │       │          │       │       │
         │       │          │       │       │
    ┌────▼──┐ ┌──▼───┐ ┌────▼───┐┌─▼───┐┌──▼──┐
    │Dashboard│KPI  │FRACAS │Servis│Arıza
    │         │      │      │Durumu│Listesi
    │         │      │      │      │
    └────┬──┘ └──┬───┘ └────┬───┘└─┬───┘└──┬──┘
         │       │          │       │       │
    ┌────▼───────▼──────────▼───────▼───────▼────┐
    │  VERI KAYNAKLAR (Seçili Project için)      │
    ├─────────────────────────────────────────────┤
    │  1. Equipment DB                            │
    │     └─→ equipment.equipment_code            │
    │                                             │
    │  2. ServiceStatus DB                        │
    │     └─→ status_record.tram_id               │
    │                                             │
    │  3. Arıza Listesi Excel                     │
    │     ├─→ logs/{p}/ariza_listesi/             │
    │     └─→ data/{p}/Veriler.xlsx (fallback)    │
    │                                             │
    │  4. Veriler.xlsx (Sayfa2)                   │
    │     └─→ data/{p}/Veriler.xlsx               │
    │                                             │
    │  5. trams.xlsx                              │
    │     └─→ data/{p}/trams.xlsx                 │
    │                                             │
    │  6. Maintenance.json                        │
    │     └─→ data/belgrad/maintenance.json       │
    └─────────────────────────────────────────────┘
```

---

## ⚠️ ÇAKIŞMALAR VE RİSKLER

### 🔴 KRITIK ÇAKILMA
**Aynı Equipment'in 3 Farklı ID'si:**
1. **Equipment.id** (DB integer): "1", "2", "3"
2. **Equipment.equipment_code** (DB string): "BEL-01", "K001"
3. **ServiceStatus.tram_id** (DB string): "BEL-01", "K001"
4. **Veriler.xlsx tram_id** (Excel string): "1", "2", "3"
5. **trams.xlsx tram_id** (Excel string): "1", "2", "3"

**SONUÇ:** 🚨 **5 farklı kimlik sistemi = Eşleştirme sorunları**

---

## 📋 PROJE SPESİFİK KAYNAKLAR

### BELGRAD Projesi
```
data/belgrad/
├─ Veriler.xlsx          (Sayfa1: sistem/tedariçci, Sayfa2: tram_id)
├─ trams.xlsx            (tram_id sütunu)
└─ maintenance.json      (KM noktaları, 70K, 140K vs)

logs/belgrad/
└─ ariza_listesi/
   └─ Ariza_Listesi_BELGRAD.xlsx (Header row 3)
```

### KAYSERI Projesi
```
data/kayseri/
├─ Veriler.xlsx          (Sayfa1: sistem, Sayfa2: tram_id: K001, K002, K003)
└─ trams.xlsx            (K001, K002, K003)

logs/kayseri/
└─ ariza_listesi/
   └─ Ariza_Listesi_KAYSERI.xlsx (178 arıza kaydı)
```

### Diğer Projeler (GEBZE, KOCAELI, İASİ, TİMIŞOARA)
```
data/{project}/
├─ Veriler.xlsx          (Template - tram_id sütunu boş)
└─ trams.xlsx            (Template - boş)

logs/{project}/
└─ ariza_listesi/
   └─ Ariza_Listesi_{PROJECT}.xlsx (Boş template)
```

---

## 🎯 SONUÇ ve ÖNERİLER

### Mevcut State
✅ **Yapılmış:**
- Multi-tenant project selection (session'da)
- Equipment tablo da project_code sütunu
- Arıza Listesi logs/ klasöründen primary
- Fallback data/ klasöründe

❌ **Eksik:**
- `trams.xlsx` dosyaları tüm projeler için dolu değil
- `Equipment.equipment_code` tutarlılığı (format değişiyor)
- `ServiceStatus.tram_id` ile `Equipment.equipment_code` eşleştirme

### ÖNERİLER
1. **Tutarlı ID Sistemi:** Tüm yerlerde aynı format kullan (equipment_code)
2. **Eksik Dosyaları Doldur:** Tüm projeler için trams.xlsx'i sync et
3. **Eşleştirme Düzelt:** Service Status ile Equipment'i doğru eşleştir
4. **Excel Köklü Referans:** Bir single source of truth belirle (DB mi yoksa Excel mi?)

---

## 🔗 İLİŞKİLİ DOSYALAR

- [routes/dashboard.py](routes/dashboard.py) - Dashboard veri kaynakları
- [routes/service_status.py](routes/service_status.py) - Servis durumu kaynakları  
- [routes/fracas.py](routes/fracas.py) - FRACAS analiz kaynakları
- [routes/kpi.py](routes/kpi.py) - KPI kaynakları
- [routes/maintenance.py](routes/maintenance.py) - Bakım veri kaynakları
- [app.py](app.py) - Yeni arıza ve diğer kaynaklar
- [models.py](models.py) - Equipment, ServiceStatus modelleri

