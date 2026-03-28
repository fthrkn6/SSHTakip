# 📊 BOZANKAYA CMS - VERİ KAYNAGI MAPPING

**Commit**: CMSv1.1  
**Tarih**: 28 Mart 2026  
**Amaç**: Sisteme dinamik olarak veri giren tüm kaynakları ve database yapılarını merkezi olarak göstermek

---

## 🗂️ GENEL BAŞKA

```
┌─────────────────────────────────────────────────────────────┐
│                  VERİ AKIŞI ÖZETİ                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Excel Dosyaları                      SQLite Database       │
│  (Dinamik Veri)    ────────────────►  (Persistent)         │
│                    ◄────────────────   └── 20+ Table       │
│                                                             │
│  ├─ data/{project}/*.xlsx             ├─ Equipment         │
│  ├─ logs/{project}/ariza_listesi/     ├─ Failure           │
│  └─ uploads/                          ├─ ServiceLog        │
│                                       ├─ Maintenance       │
│                                       └─ 17+ More          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ EXCEL VERİ KAYNARLARI (Dinamik)

### 📁 Ana Dosya Yapısı

```
bozankaya_ssh_takip/
├── data/
│   ├── belgrad/
│   │   ├── Veriler.xlsx           ✅ AKTIF - Tramvay listesi
│   │   ├── Güncel*.xlsx           ✅ AKTIF - Yedek parçalar
│   │   ├── FRACAS.xlsx            ⚠️  FALLBACK
│   │   └── km_data.xlsx           ❓ OPSIYONEL
│   │
│   ├── kayseri/
│   │   ├── Veriler.xlsx           ✅ AKTIF - Tramvay listesi
│   │   ├── Güncel*.xlsx           ✅ AKTIF - Yedek parçalar
│   │   └── FRACAS.xlsx            ⚠️  FALLBACK
│   │
│   ├── kocaeli/
│   │   ├── Veriler.xlsx           ✅ AKTIF
│   │   └── Güncel*.xlsx           ✅ AKTIF
│   │
│   ├── gebze/
│   │   ├── Veriler.xlsx           ✅ AKTIF
│   │   └── Güncel*.xlsx           ✅ AKTIF
│   │
│   ├── istanbul/
│   │   ├── Veriler.xlsx           ✅ AKTIF
│   │   ├── km_data.xlsx           ✅ AKTIF
│   │   ├── service_status.xlsx    ✅ AKTIF
│   │   └── Güncel*.xlsx           ✅ AKTIF
│   │
│   ├── kocaeli/
│   │   ├── Veriler.xlsx           ⚠️  HAZIRLANMA
│   │   └── FRACAS.xlsx            ⚠️  HAZIRLANMA
│   │
│   └── timisoara/
│       ├── Veriler.xlsx           ⚠️  HAZIRLANMA
│       └── km_data.xlsx           ⚠️  HAZIRLANMA
│
└── logs/
    ├── belgrad/ariza_listesi/
    │   ├── Ariza_Listesi_BELGRAD.xlsx        ✅ PRIMARY
    │   ├── Fracas_BELGRAD.xlsx               ⚠️  SECONDARY
    │   └── Ariza_Listesi_BELGRAD_EXPORT.xlsx ✅ ARCHIVE
    │
    ├── kayseri/ariza_listesi/
    │   ├── Ariza_Listesi_KAYSERI.xlsx        ✅ PRIMARY
    │   └── Fracas_KAYSERI.xlsx               ⚠️  SECONDARY
    │
    ├── istanbul/ariza_listesi/
    │   ├── Ariza_Listesi_ISTANBUL.xlsx       ✅ PRIMARY
    │   └── Fracas_ISTANBUL.xlsx              ⚠️  SECONDARY
    │
    └── service_logs/              (Future)
        └── *.xlsx                 ❓ PLANNED
```

---

## 2️⃣ EXCEL DOSYALARI DETAYLI MAPPING

### 📄 **Veriler.xlsx** (Primary Data Source)

| **Proje** | **Konum** | **Sayfa** | **Header** | **Kullanım** | **Veri Türü** |
|-----------|-----------|-----------|-----------|------------|--------------|
| belgrad | `data/belgrad/` | Sayfa2 | Row 0 | Tramvay listesi | Statik |
| kayseri | `data/kayseri/` | Sayfa2 | Row 0 | Tramvay listesi | Statik |
| istanbul | `data/istanbul/` | Sayfa2 | Row 0 | Tramvay listesi | Statik |
| gebze | `data/gebze/` | Sayfa2 | Row 0 | Tramvay listesi | Statik |
| timisoara | `data/timisoara/` | (Planned) | - | - | - |

**Sütunlar:**
- `tram_id` / `Araç No` / `Vehicle Number` → Equipment.equipment_code
- `model` / `Model` → Equipment.model
- `manufacturer` → Equipment.manufacturer
- `installation_date` / `Kurulum Tarihi` → Equipment.installation_date
- `status` → Equipment.status
- `location` → Equipment.location

**Okunduğu Yerler:**
- [app.py:615](app.py#L615) - Sistem yükleme (init form)
- [routes/dashboard.py:1582](routes/dashboard.py#L1582) - Tramvay synchronize
- [sync_fracas_data.py:50](sync_fracas_data.py#L50) - Veritabanı sync

---

### 📄 **Ariza_Listesi_*.xlsx** (Failure Records - PRIMARY)

| **Proje** | **Dosya Adı** | **Konum** | **Sheet** | **Header** | **Durumu** |
|-----------|---------------|-----------|-----------|-----------|-----------|
| belgrad | Ariza_Listesi_BELGRAD.xlsx | `logs/belgrad/ariza_listesi/` | Ariza Listesi | Row 3 | ✅ AKTIF |
| kayseri | Ariza_Listesi_KAYSERI.xlsx | `logs/kayseri/ariza_listesi/` | Ariza Listesi | Row 3 | ✅ AKTIF |
| istanbul | Ariza_Listesi_ISTANBUL.xlsx | `logs/istanbul/ariza_listesi/` | Ariza Listesi | Row 3 | ✅ AKTIF |

**Dinamik Sütun Haritası** (Exact column names found in Excel):
```python
# Arama yöntemi: Regex pattern matching
Araç No / Vehicle Number / Araç Numarası
  ├─ Exact: "Araç No"
  ├─ Partial: "Araç" + "No" / "vehicle" + "number"
  └─ Fallback: İlk alfanümerik sütun

Sistem / System
  ├─ "Sistem"
  └─ "Alt Sistem" hariç (partial match)

Tamir Süresi / Repair Time (MTTR)
  ├─ "Tamir Süresi"
  ├─ "MTTR (dk)" / "MTTR (Dakika)"
  └─ "Downtime" (fallback)

Tedarikçi / Supplier
  ├─ "Tedarikçi"
  └─ "Supplier"

Arıza Sınıfı / Failure Class
  ├─ "Arıza Sınıfı"
  ├─ "Failure Class"
  └─ "Severity"
```

**Okunduğu Yerler:**
- [routes/fracas.py:144-197](routes/fracas.py#L144) - FRACAS dashboard
- [routes/dashboard.py:827-1020](routes/dashboard.py#L827) - API /failures endpoint
- [routes/dashboard.py:329-415](routes/dashboard.py#L329) - MTTR hesaplama
- [app.py:492-610](app.py#L492) - Sistem seçimi / Arıza görüntüleme

**Sütun Sayısı**: ~30 kolon  
**Veri Sayısı**: 15-50 arıza kaydı (proje depthine göre)

---

### 📄 **Fracas_*.xlsx** (FRACAS Raporları - SECONDARY)

| **Proje** | **Dosya Adı** | **Konum** | **Sheet** | **Header** | **Durumu** |
|-----------|---------------|-----------|-----------|-----------|-----------|
| belgrad | Fracas_BELGRAD.xlsx | `data/belgrad/` | FRACAS | Row 0 | ⚠️ FALLBACK |
| belgrad | Fracas_BELGRAD.xlsx | `logs/belgrad/ariza_listesi/` | FRACAS | Row 3 | ✅ PRIMARY |
| kayseri | Fracas_KAYSERI.xlsx | `logs/kayseri/ariza_listesi/` | FRACAS | Row 3 | ✅ PRIMARY |
| istanbul | Fracas_ISTANBUL.xlsx | `logs/istanbul/ariza_listesi/` | FRACAS | Row 3 | ✅ PRIMARY |

**Okunduğu Yerler:**
- [routes/fracas.py:93-145](routes/fracas.py#L93) - FRACAS data loading
- [routes/dashboard.py:800-850](routes/dashboard.py#L800) - API failures endpoint

---

### 📄 **Güncel*.xlsx** (Spare Parts Inventory)

| **Proje** | **Pattern** | **Konum** | **Durumu** |
|-----------|------------|----------|----------|
| belgrad | `Güncel*.xlsx` | `data/belgrad/` | ✅ AKTIF |
| kayseri | `Güncel*.xlsx` | `data/kayseri/` | ✅ AKTIF |
| istanbul | `Güncel*.xlsx` | `data/istanbul/` | ✅ AKTIF |

**Sütunlar**:
- `Bileşen numarası` → Part code
- `Nesne kısa metni` → Part description
- `Stok` / `Quantity` → Inventory level

**Okunduğu Yerler:**
- [app.py:128-200](app.py#L128) - `load_parts_cache()` → Global cache
- [routes/api.py:96-110](routes/api.py#L96) - `/api/equipment-parts/` endpoint

**Cache Policy**: 
- Dosya yüklendiğinde cache'lenir
- Kullanıcı başına bir kere (global `_parts_cache`)
- TTL: Session süresi boyunca

---

### 📄 **km_data.xlsx** (Kilometre Tracking)

| **Proje** | **Konum** | **Durumu** |
|-----------|----------|----------|
| istanbul | `data/istanbul/km_data.xlsx` | ✅ AKTIF |
| timisoara | `data/timisoara/km_data.xlsx` | ⚠️ PLANNED |

**Sütunlar**:
- Tramvay ID / Araç No
- Günlük KM
- Aylık KM (aggregate)
- Tarih

**Okunduğu Yerler**:
- [routes/tramvay_km.py](routes/tramvay_km.py) (if exists) - KM tracking page

---

### 📄 **service_status.xlsx** (Daily Service Status Log)

| **Proje** | **Konum** | **Durumu** |
|-----------|----------|----------|
| istanbul | `data/istanbul/service_status.xlsx` | ✅ AKTIF |

**Sütunlar**:
- Tarih / Date
- Araç No
- Status (Servis, Servis Dışı, İşletme Kaynaklı, vb)
- Malzeme Nedeni

**Okunduğu Yerler**:
- [utils_service_status.py](utils_service_status.py) - Service status calculations
- [routes/dashboard.py:*](routes/dashboard.py) - Dashboard service status display

---

## 3️⃣ DATABASE TABLOLARI (20+ Tablo)

### 📌 **CORE TABLES** (Ana Veri Modelleri)

#### **Equipment** (Ekipman/Tramvay)
```
PRIMARY KEY: id
COLUMNS:
  ├─ equipment_code: VARCHAR(50) - Tramvay numarası (1531, 1532, ...)
  ├─ name: VARCHAR(100) - Tramvay adı
  ├─ project_code: VARCHAR(50) - Proje (belgrad, kayseri, ...)
  ├─ equipment_type: VARCHAR(50) - Type (tramvay, modül, parça)
  ├─ manufacturer: VARCHAR(100) - Üretici
  ├─ model: VARCHAR(100) - Model numarası
  ├─ status: VARCHAR(20) - aktif, bakim, ariza, depo
  ├─ current_km: INTEGER - Mevcut kilometre
  ├─ total_maintenance_cost: FLOAT - Toplam bakım maliyeti
  ├─ mtbf_hours: FLOAT - Mean Time Between Failures
  ├─ mttr_hours: FLOAT - Mean Time To Repair
  ├─ availability_rate: FLOAT - (0-100%)
  ├─ parent_id: FOREIGN KEY - Hiyerarşik ilişki
  └─ created_at: DATETIME

RELATIONSHIPS:
  ├─ failures: 1→Many (Failure table)
  ├─ work_orders: 1→Many (WorkOrder table)
  ├─ maintenance_plans: 1→Many (MaintenancePlan table)
  └─ children: 1→Many (Equipment table - recursive)

VERİ KAYNAĞI:
  ├─ Excel (Veriler.xlsx) → Manual import
  ├─ sync_fracas_data.py → Excel-to-DB sync
  └─ routes/dashboard.py → Real-time updates
```

---

#### **Failure** (Arıza Kayıtları)
```
PRIMARY KEY: id
COLUMNS:
  ├─ failure_code: VARCHAR(50) - FRACAS ID (BEL25-001, ...)
  ├─ equipment_id: FOREIGN KEY → Equipment.id
  ├─ title: VARCHAR(200) - Arıza başlığı
  ├─ description: TEXT - Detaylı açıklama
  ├─ severity: VARCHAR(20) - Kritik, Yüksek, Orta, Düşük
  ├─ failure_type: VARCHAR(50) - Elektrik, Mekanik, vb
  ├─ failure_mode: VARCHAR(100) - FMEA modu
  ├─ root_cause: VARCHAR(200) - Kök neden
  ├─ status: VARCHAR(20) - acik, devam_ediyor, cozuldu, kapandi
  ├─ project_code: VARCHAR(50) - Proje kodu
  ├─ detected_date: DATETIME - Tespit tarihi
  ├─ resolved_date: DATETIME - Çözüm tarihi
  ├─ downtime_minutes: INTEGER - İnişte süre (dakika)
  ├─ repair_cost: FLOAT - Tamir maliyeti
  └─ created_at: DATETIME

VERİ KAYNAĞI:
  ├─ Excel (Ariza_Listesi_*.xlsx) → READ-ONLY
  ├─ Excel (Fracas_*.xlsx) → READ-ONLY
  └─ Manual entry (/yeni-ariza-bildir) → INSERT
```

---

#### **WorkOrder** (İş Emirleri)
```
PRIMARY KEY: id
COLUMNS:
  ├─ work_order_code: VARCHAR(50)
  ├─ equipment_id: FOREIGN KEY
  ├─ title: VARCHAR(200)
  ├─ description: TEXT
  ├─ priority: VARCHAR(20)
  ├─ status: VARCHAR(20) - planned, in_progress, completed, cancelled
  ├─ scheduled_date: DATETIME
  ├─ completed_date: DATETIME
  ├─ estimated_hours: FLOAT
  ├─ actual_hours: FLOAT
  └─ assigned_to: FOREIGN KEY → User.id

VERİ KAYNAĞI:
  └─ Manual entry (/work-orders) → INSERT/UPDATE
```

---

#### **MaintenancePlan** (Bakım Planları)
```
PRIMARY KEY: id
COLUMNS:
  ├─ maintenance_code: VARCHAR(50)
  ├─ equipment_id: FOREIGN KEY
  ├─ maintenance_type: VARCHAR(50) - predictive, preventive, corrective
  ├─ frequency_type: VARCHAR(20) - km, hours, calendar_days
  ├─ frequency_value: FLOAT
  ├─ last_maintenance_date: DATETIME
  ├─ next_due_date: DATETIME
  ├─ is_active: BOOLEAN
  └─ estimated_duration: FLOAT

VERİ KAYNAĞI:
  └─ Manual entry (Maintenance Planning) → INSERT/UPDATE
```

---

#### **User** (Kullanıcılar)
```
PRIMARY KEY: id
COLUMNS:
  ├─ username: VARCHAR(80) - Unique
  ├─ email: VARCHAR(120) - Unique
  ├─ password_hash: VARCHAR(255)
  ├─ full_name: VARCHAR(100)
  ├─ role: VARCHAR(20) - admin, saha, muhendis, teknisyen
  ├─ role_id: FOREIGN KEY → Role.id (new system)
  ├─ assigned_projects: TEXT (JSON) - ["belgrad", "kayseri"]
  ├─ department: VARCHAR(50)
  ├─ skills: TEXT (JSON) - ["elektrik", "mekanik"]
  ├─ skill_level: VARCHAR(20) - junior, mid, senior, expert
  ├─ is_active: BOOLEAN
  └─ created_at: DATETIME

VERİ KAYNAĞI:
  └─ Manual entry (/admin/users) → INSERT/UPDATE/DELETE
```

---

### 📌 **REPORTING TABLES** (Raporlama Tabloları)

#### **AvailabilityMetrics** (Mevcut Oranı Hesaplamaları)
```
PRIMARY KEY: id
COLUMNS:
  ├─ equipment_id: FOREIGN KEY
  ├─ date: DATE
  ├─ availability_percentage: FLOAT
  ├─ planned_downtime: INTEGER
  ├─ unplanned_downtime: INTEGER
  ├─ total_uptime: INTEGER

VERİ KAYNAĞI:
  └─ Calculated from DowntimeRecord (nightly batch job)
```

---

#### **ServiceLog** (Servis Günlüğü)
```
PRIMARY KEY: id
COLUMNS:
  ├─ equipment_id: FOREIGN KEY
  ├─ service_date: DATE
  ├─ service_type: VARCHAR(50) - servis, servis_disi, isleme_kaynaklı
  ├─ next_service_km: FLOAT
  ├─ notes: TEXT
  ├─ created_by: FOREIGN KEY → User.id

VERİ KAYNAĞI:
  ├─ Excel (service_status.xlsx) → import
  └─ Manual entry (Service Logger) → INSERT/UPDATE
```

---

#### **RootCauseAnalysis** (Kök Neden Analizi)
```
PRIMARY KEY: id
COLUMNS:
  ├─ failure_id: FOREIGN KEY
  ├─ equipment_id: FOREIGN KEY
  ├─ rca_code: VARCHAR(50)
  ├─ root_cause: TEXT
  ├─ contributing_factors: TEXT (JSON)
  ├─ corrective_actions: TEXT
  ├─ preventive_actions: TEXT
  ├─ analysis_date: DATETIME
  ├─ analyzed_by: FOREIGN KEY → User.id

VERİ KAYNAĞI:
  └─ Manual entry (RCA page) → INSERT/UPDATE
```

---

### 📌 **CONFIGURATION TABLES** (Konfigürasyon)

#### **Role** (Roller)
```
PRIMARY KEY: id
COLUMNS:
  ├─ name: VARCHAR(50) - Unique
  ├─ description: VARCHAR(255)
  ├─ permissions: TEXT (JSON)
  └─ created_at: DATETIME

VERİ KAYNAĞI:
  └─ seed_perms.py → Initialization script
```

---

#### **Permission** (İzinler)
```
PRIMARY KEY: id
COLUMNS:
  ├─ page_name: VARCHAR(100)
  ├─ description: VARCHAR(255)
  └─ category: VARCHAR(50)

VERİ KAYNAĞI:
  └─ seed_permissions.py → Initialization script
```

---

## 4️⃣ VERİ AKIŞI DİYAGRAMLARI

### 🔄 **Excel → Database Sync Flow**

```
┌─────────────────────────────────────────────────────────────┐
│ EXCEL DOSYALARI (logs/ ve data/ klasörleri)                 │
│                                                             │
│ ├─ Ariza_Listesi_*.xlsx                                    │
│ ├─ Fracas_*.xlsx                                            │
│ ├─ Veriler.xlsx (Sayfa2)                                   │
│ └─ Güncel*.xlsx                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    (Pandas read_excel)
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ PYTHON PROCESSING (app.py & routes/*)                       │
│                                                             │
│ ├─ load_parts_cache() → Cache'le (Güncel*.xlsx)           │
│ ├─ load_ariza_listesi_data() → Parse (Ariza_Listesi)     │
│ ├─ load_fracas_data() → Parse (Fracas)                   │
│ ├─ sync_fracas_data() → SQL INSERT (Equipment, Failure)   │
│ └─ calculate_fleet_mttr() → Compute metrics                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    (db.session.add/commit)
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ SQLite DATABASE (ssh_takip_bozankaya.db)                   │
│                                                             │
│ ├─ equipment (25-30 records/proje)                         │
│ ├─ failure (50-100 records)                                │
│ ├─ service_log (500+ records)                              │
│ └─ maintenance_plan (100+ records)                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                      (SQLAlchemy ORM)
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ FLASK ROUTES & TEMPLATES (Web UI)                           │
│                                                             │
│ ├─ /dashboard → Equipment.query.all()                      │
│ ├─ /fracas → Failure.query.filter()                        │
│ ├─ /api/failures → Pandas (Excel OR DB)                    │
│ └─ /work-orders → WorkOrder.query.filter()                 │
└─────────────────────────────────────────────────────────────┘
```

---

### 🔌 **API Endpoints Data Sources**

```
GET /api/projects
  ├─ Source: Database (ProjecConfig table or hardcoded)
  └─ Returns: JSON ['belgrad', 'kayseri', 'istanbul', ...]

GET /api/equipment/<project>
  ├─ Source: Database (Equipment table) + Cache
  │   └─ Equipment.query.filter_by(project_code=project)
  └─ Returns: JSON [equipment objects]

GET /api/equipment-parts/<equipment_code>
  ├─ Source: Excel (Güncel*.xlsx) → Global Cache
  │   └─ load_parts_cache(project)[search_by_code]
  └─ Returns: JSON [spare parts]

GET /api/failures[/<equipment_code>]
  ├─ Source: DUAL
  │   ├─ PRIMARY: Excel (logs/{project}/ariza_listesi/)
  │   │   ├─ Ariza_Listesi_*.xlsx (Sheet: Ariza Listesi)
  │   │   └─ Fracas_*.xlsx (Sheet: FRACAS)
  │   └─ FALLBACK: Database (Failure table)
  └─ Returns: JSON [failure objects]

GET /api/statistics/mttr
  ├─ Source: COMPUTED
  │   ├─ Excel (Ariza_Listesi_*.xlsx) → MTTR column
  │   └─ Pandas groupby + mean calculation
  └─ Returns: JSON {mttr_minutes, count, breakdown_by_supplier}

GET /api/bakim-tablosu-transpose
  ├─ Source: Database (Equipment + MaintenancePlan)
  │   └─ Equipment.query + maintenance_plans relationship
  └─ Returns: JSON [matrix of equipment vs maintenance points]

GET /performance/health
  ├─ Source: Database (all tables)
  │   ├─ Record count per table
  │   ├─ Database size
  │   └─ Query performance metrics
  └─ Returns: JSON {db_health, query_times}
```

---

## 5️⃣ DINAMIK VERİ ÇEKME MEKANIZMLARI

### ⚡ **Global Cache System** (`_parts_cache`)

```python
# İnitialize: app.py:128
_parts_cache = {}
_parts_cache_time = {}

# Load: app.py:161-200
def load_parts_cache(project=None):
    # Güncel*.xlsx dosyasını oku
    # Cache'e koy (application lifetime)
    # Return cached data

# Usage:
# Templates'ten: {{ parts_cache[project] }}
# API'den: GET /api/equipment-parts/
```

**Cache Policy**:
- Scope: Application global
- TTL: Session lifetime (3600 saniye)
- Update: Manual trigger veya page reload
- Fallback: Database (if Excel not found)

---

### ⚡ **Session-Based Project Selection**

```python
# app.py:250-280
@app.before_request
def handle_project_selection():
    if 'current_project' not in session:
        session['current_project'] = 'belgrad'  # default
    # Tüm routes'da kullanılabilir
    
# Usage:
# current_project = session.get('current_project', 'belgrad')
# file_path = f"logs/{current_project}/ariza_listesi/..."
```

---

### ⚡ **Excel File Discovery (Fallback Pattern)**

```python
# Pattern 1: Arıza Listesi dosyası arama
ariza_listesi_dir = f"logs/{project}/ariza_listesi/"

# 1. Ariza_Listesi_*.xlsx ara
for file in os.listdir(ariza_listesi_dir):
    if 'Ariza_Listesi' in file and file.endswith('.xlsx'):
        file_path = os.path.join(ariza_listesi_dir, file)
        use_sheet = 'Ariza Listesi'
        header = 3
        break

# 2. Fallback: Fracas_*.xlsx ara
if not file_path:
    for file in os.listdir(ariza_listesi_dir):
        if 'Fracas' in file and file.endswith('.xlsx'):
            file_path = os.path.join(ariza_listesi_dir, file)
            use_sheet = 'FRACAS'
            header = 3
            break

# 3. Final fallback: data/{project}/Veriler.xlsx
if not file_path:
    file_path = f"data/{project}/Veriler.xlsx"
    use_sheet = 'Veriler'
    header = 0
```

---

### ⚡ **Dynamic Column Name Matching**

```python
# Problem: Excel sütun adları farklı projeler/dosyalarda değişiyor
# Solution: Fuzzy column matching

def get_column(df, possible_names):
    """Olası kolon isimlerinden birini bul"""
    for col in df.columns:
        col_clean = col.lower().replace('\n', ' ').strip()
        for name in possible_names:
            if name.lower() in col_clean:
                return col
    return None

# Usage:
arac_col = get_column(df, [
    'Araç No', 'araç numarası', 'vehicle number', 
    'tram_id', 'tramvay'
])
```

---

## 6️⃣ VERI GÜNCELLEMESİ ÖZETİ

### 🔄 **Manual Updates**

| Sayfa | URL | Veri Kaynağı | Update Method |
|-------|-----|-------------|---------------|
| Yeni Arıza Bildir | `/yeni-ariza-bildir` | Excel (Ariza Listesi) | POST Form → Excel Write |
| Tramvay KM | `/tramvay-km` | Excel (km_data.xlsx) | POST Form → Excel Write |
| Servis Durumu | `/servis-durumu` | Excel + Database | POST Form → Both |
| Bakım Planlaması | `/bakim-planlama` | Database | POST Form → DB Insert |
| Admin Panel | `/admin/*` | Database | POST Form → DB CRUD |

---

### 🤖 **Automated Batch Updates**

| Script | Frequency | Kaynak | Hedef |
|--------|-----------|--------|-------|
| `sync_fracas_data.py` | Manual | Excel (FRACAS) | Equipment, Failure tables |
| `sync_equipment_from_logger.py` | Manual | Excel (Veriler) | Equipment table |
| `sync_excel_to_equipment.py` | Manual | Excel | Equipment + sync |
| Dashboard sync middleware | Per request | Excel | Memory cache |

---

## 7️⃣ PROJELERİN VERİ DURUMU

### 📊 **Belgrad**
```
✅ FULLY OPERATIONAL
├─ data/belgrad/
│   ├─ Veriler.xlsx (25 tram)
│   ├─ Güncel*.xlsx (yedek parçalar)
│   └─ FRACAS.xlsx
├─ logs/belgrad/ariza_listesi/
│   ├─ Ariza_Listesi_BELGRAD.xlsx (23 arıza)
│   └─ Fracas_BELGRAD.xlsx
└─ Database: ~500 records fully synced
```

### 📊 **Kayseri**
```
✅ FULLY OPERATIONAL
├─ data/kayseri/
│   ├─ Veriler.xlsx (11 tram)
│   ├─ Güncel*.xlsx
│   └─ FRACAS.xlsx
├─ logs/kayseri/ariza_listesi/
│   ├─ Ariza_Listesi_KAYSERI.xlsx
│   └─ Fracas_KAYSERI.xlsx
└─ Database: ~200 records
```

### 📊 **İstanbul**
```
✅ FULLY OPERATIONAL
├─ data/istanbul/
│   ├─ Veriler.xlsx (11 tram)
│   ├─ km_data.xlsx (günlük KM)
│   ├─ service_status.xlsx
│   └─ Güncel*.xlsx
├─ logs/istanbul/ariza_listesi/
│   ├─ Ariza_Listesi_ISTANBUL.xlsx
│   └─ Fracas_ISTANBUL.xlsx
└─ Database: ~300 records
```

### 📊 **Gebze**
```
⚠️ PARTIAL
├─ data/gebze/
│   ├─ Veriler.xlsx (25 tram)
│   ├─ Güncel*.xlsx
│   └─ (NO FRACAS)
└─ Database: ~100 records
```

### 📊 **Kocaeli**
```
⚠️ PREPARATION PHASE
├─ (Veriler.xlsx preparing)
├─ (No FRACAS data yet)
└─ Database: <50 records
```

### 📊 **Timisoara**
```
⚠️ PLANNED
├─ (Data structure planned)
└─ Database: (empty)
```

---

## 8️⃣ DATABASE ÖNEMLİ QUERIES

### 📌 Key Query Patterns

```python
# 1. Equipment by project
Equipment.query.filter_by(project_code='belgrad').all()

# 2. Recent failures
Failure.query.order_by(Failure.created_at.desc()).limit(10).all()

# 3. Equipment with open failures
Equipment.query.join(Failure).filter(Failure.status=='acik').all()

# 4. MTTR trend by supplier (from Failure table)
Failure.query.filter_by(project_code='belgrad')\
  .group_by('supplier')\
  .avg('repair_time')

# 5. Availability by equipment
Equipment.query.filter_by(project_code='belgrad')\
  .order_by(Equipment.availability_rate.desc())

# 6. Maintenance plans due (from MaintenancePlan)
MaintenancePlan.query.filter(
    MaintenancePlan.next_due_date < date.today(),
    MaintenancePlan.is_active == True
).all()

# 7. User permissions
RolePermission.query.filter_by(role='saha').all()
```

---

## 🎯 SONUÇ VE ÖNERILER

### ✅ **Şu Anda İyi Çalışan**
- Excel → Database sync mekanizması
- Multi-project support (7 proje)
- Dynamic column name matching
- Session-based project filtering
- Role-based access control

### ⚠️ **İyileştirilmesi Gereken**
1. **Database Indexing** - Hız için gerekli (bkz: OPTIMIZATION_PRIORITIES.md)
2. **Caching Strategy** - Redis entegrasyonu
3. **Async Updates** - Celery ile batch processing
4. **Data Validation** - Input/output schema validation
5. **Audit Logging** - Tüm Excel/DB güncellemeler kaydedilmeli

### 🔮 **Future Enhancements**
- Real-time Excel monitoring (pymon)
- API versioning (/api/v1, /api/v2)
- Multi-database support (PostgreSQL fallback)
- Data warehouse (analytics cube)
- REST API documentation (Swagger/OpenAPI)

---

**Son güncellenme**: 28 Mart 2026  
**Hazırlanmış**: GitHub Copilot + CMSv1.1 Analysis
