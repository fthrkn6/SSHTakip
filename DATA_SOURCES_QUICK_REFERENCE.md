# 🚀 VERI KAYNARLARI - QUICK REFERENCE GUIDE

**Status**: CMSv1.1  
**Amaç**: Hızlı lookup - Hangi veri nerede? Nasıl akışı? Kodu nerede?

---

## 🔍 HIZLI ARAMA

### 1. "Tramvay listesini nerede alıyoruz?"
```
✅ Kaynak: data/{project}/Veriler.xlsx (Sayfa2)
📍 Okuma yeri: app.py:615, routes/dashboard.py:1582
🔄 Senkronizasyon: sync_fracas_data.py
💾 Database: Equipment table (100-150 records/system)
⏱️ Zaman: ~50-100ms

Sütun Adları:
├─ tram_id / Araç No / Vehicle Number
├─ model
├─ manufacturer
└─ installation_date
```

---

### 2. "Arızaları nerede alıyoruz?"
```
✅ BIRINCIL: logs/{project}/ariza_listesi/Ariza_Listesi_*.xlsx
📍 Sayfası: "Ariza Listesi" (Header: Row 3)
📍 Okuma yeri: 
   ├─ routes/fracas.py:144-197 (FRACAS dashboard)
   ├─ routes/dashboard.py:827-1020 (API /failures)
   └─ app.py:492-610 (Sistem seçimi)

⚠️ FALLBACK 1: logs/{project}/Fracas_*.xlsx
   └─ Sheet: "FRACAS" (Header: Row 3)

⚠️ FALLBACK 2: data/{project}/Veriler.xlsx
   └─ Sheet: "Sayfa2" (Header: Row 0)

💾 Database: Failure table (200-500 records total)
⏱️ Zaman: ~100-300ms (Excel read + parse)

Kritik Sütunlar (Dinamik Arama):
├─ Araç No → Equipment.equipment_code
├─ Sistem → Equipment.location
├─ Tamir Süresi → MTTR_minutes
├─ Tedarikçi → supplier_name
├─ Arıza Sınıfı → severity
└─ Tarih → disaster_timestamp
```

---

### 3. "Yedek parçaları nerede alıyoruz?"
```
✅ Kaynak: data/{project}/Güncel*.xlsx
📍 Okuma yeri: app.py:128-200 (load_parts_cache function)
🔄 Cache: Global _parts_cache (application lifetime)
💾 Database: SparePartInventory table
⏱️ Zaman: ~10ms (cached) / ~100ms (first load)

Sütun Adları:
├─ Bileşen numarası → part_code
├─ Nesne kısa metni → part_description
└─ Stok → quantity_on_hand

API Endpoint: GET /api/equipment-parts/{equipment_code}
```

---

### 4. "KM verilerini nerede alıyoruz?"
```
✅ Kaynak: data/{project}/km_data.xlsx
📍 Projeler: istanbul, timisoara (planned)
📍 Sütunlar:
   ├─ Araç No / tram_id
   ├─ Günlük KM
   └─ Tarih

💾 Database: MeterReading table (500+ records)
🔄 Güncelleme: Manual (upload feature)
⏱️ Zaman: ~50ms
```

---

### 5. "Servis durumunu nerede alıyoruz?"
```
✅ Kaynak: data/{project}/service_status.xlsx
📍 Projeler: istanbul (primarily)
📍 Sütunlar:
   ├─ Tarih
   ├─ Araç No
   ├─ Status (Servis, Servis Dışı, İşletme Kaynaklı)
   └─ Malzeme Nedeni

💾 Database: ServiceLog table (800+ records)
📍 Okuma yeri: utils_service_status.py
🔄 Güncelleme: Manual (upload) + Dashboard status field
⏱️ Zaman: ~100ms
```

---

## 📍 PROJE BAŞINA VERİ DURUMU

### Belgrad (25 tramvay) ✅ FULLY OPERATIONAL
```
Veriler.xlsx:               ✅ Aktif (25 tram)
Güncel_*.xlsx:              ✅ Aktif (yedek parçalar)
Ariza_Listesi_BELGRAD.xlsx: ✅ Aktif (23 record)
Fracas_BELGRAD.xlsx:        ✅ Aktif (backup)
Database Equipment:         ✅ 25 synced
Database Failure:           ✅ 100+ synced
```

### Kayseri (11 tramvay) ✅ FULLY OPERATIONAL
```
Veriler.xlsx:               ✅ Aktif (11 tram)
Güncel_*.xlsx:              ✅ Aktif
Ariza_Listesi_KAYSERI.xlsx: ✅ Aktif
Fracas_KAYSERI.xlsx:        ✅ Aktif
Database:                   ✅ Synced
```

### İstanbul (11 tramvay) ✅ FULLY OPERATIONAL
```
Veriler.xlsx:               ✅ Aktif (11 tram)
km_data.xlsx:               ✅ Aktif (günlük KM)
service_status.xlsx:        ✅ Aktif
Güncel_*.xlsx:              ✅ Aktif
Ariza_Listesi_ISTANBUL.xlsx:✅ Aktif
Database:                   ✅ Synced
```

### Gebze (25 tramvay) ⚠️ PARTIAL
```
Veriler.xlsx:               ✅ Aktif (25 tram)
Güncel_*.xlsx:              ✅ Aktif
FRACAS:                     ❌ YOK
Database:                   ⚠️ Partial
```

### Kocaeli, Timisoara
```
Status:                     🔵 HAZIRLANMA AŞAMASINDA
```

---

## 🔗 KOD KONUMLARI (Key Reference)

### app.py
```python
# Line 128-200:    load_parts_cache() - Güncel*.xlsx reader
# Line 169:        pd.read_excel(part_file)
# Line 215-220:    Database configuration
# Line 365:        init_excel_files() call
# Line 492-610:    Sistem seçimi ve Veriler.xlsx yükleme
# Line 600:        load_workbook() for Excel reading
```

### routes/dashboard.py
```python
# Line 329-415:    calculate_fleet_mttr() - MTTR hesaplama
# Line 780-1020:   get_equipment_failures() endpoint
# Line 814-850:    Excel dosya arama (Ariza_Listesi fallback)
# Line 987:        API arızaları endpoint
```

### routes/fracas.py
```python
# Line 79-145:     load_fracas_data() function
# Line 144-197:    load_ariza_listesi_data() function
# Line 195-238:    index() route - FRACAS dashboard
# Line 79:         get_column() - Fuzzy matching
```

### models.py
```python
# Line 200-300:    Equipment table definition
# Line 330-450:    Failure table definition
# Line 450+:       WorkOrder, MaintenancePlan, ServiceLog, etc.
```

### utils_*.py (20+ files)
```python
utils_fracas_writer.py:             Excel FRACAS writing
utils_excel_grid_manager.py:         Excel grid operations
utils_service_status.py:             Service status calculations
utils_km_excel_logger.py:            KM tracking
utils_performance.py:                Cache management
```

---

## 📊 VERİ AKIŞI DIYAGRAMLARI

### Excel → Display (Synchronous)
```
User visits /fracas
    ↓
Flask route calls load_ariza_listesi_data()
    ↓
Function searches:
  1. logs/{project}/ariza_listesi/Ariza_Listesi_*.xlsx
  2. logs/{project}/Fracas_*.xlsx
  3. data/{project}/Veriler.xlsx (fallback)
    ↓
Pandas reads Excel → DataFrame
    ↓
Python processes data:
  - Dynamic column matching
  - Type conversions
  - Filtering/sorting
    ↓
Render Jinja2 template with data
    ↓
Return HTML (100-300ms total)
```

### Excel → Database (Batch Sync)
```
User runs sync_fracas_data.py
    ↓
Read Excel (FRACAS sheet)
    ↓
Parse data → Equipment, Failure objects
    ↓
db.session.add() all objects
    ↓
db.session.commit()
    ↓
Equipment table updated
Failure table updated
    ↓
Next /dashboard call sees updated data
```

### Cache Pattern (Spare Parts)
```
First request:
  load_parts_cache() 
    ├─ Read Güncel_*.xlsx
    ├─ Parse & store in _parts_cache[project]
    └─ Return parts list

Subsequent requests:
  load_parts_cache()
    ├─ Check _parts_cache[project]
    ├─ Found → Return immediately (10ms)
    └─ Cache until app restart

Manual reset: Clear _parts_cache at session start
```

---

## 🎯 YAYGIN SORULAR & CEVAPLAR

### Q: "Hangi dosyalar hangi projeyi temsil ediyor?"
A:
```
Proje Kodu (session['current_project']):
├─ belgrad   → data/belgrad/,  logs/belgrad/ariza_listesi/
├─ kayseri   → data/kayseri/,  logs/kayseri/ariza_listesi/
├─ istanbul  → data/istanbul/, logs/istanbul/ariza_listesi/
├─ gebze     → data/gebze/,    logs/gebze/ariza_listesi/ (empty)
├─ kocaeli   → (preparing)
└─ timisoara → (preparing)

Project list endpoint: /api/projects (hardcoded or DB config)
```

---

### Q: "Veritabanı vs Excel - hangisi önce güncellenıyor?"
A:
```
Priority: EXCEL ALWAYS PRIMARY (read-only)

User enters failure:
  1. POST /yeni-ariza-bildir
  2. Save to Excel (Ariza_Listesi_*.xlsx) ← PRIMARY
  3. Optional: Also save to DB (for backup)
  
Dashboard shows failure:
  1. Check Excel first (logs/*/ariza_listesi/)
  2. If Excel fail → Fallback to Database
  3. Real-time: Always read Excel

Sync mechanism:
  - Manual: sync_fracas_data.py (admin runs)
  - Automatic: None currently (on-demand read)
```

---

### Q: "Dinamik sütun adları nasıl eşleştiriliyir?"
A:
```
Pattern matching in routes/fracas.py:get_column():

def get_column(df, possible_names):
    for col in df.columns:
        col_clean = col.lower().replace('\n', ' ').strip()
        for name in possible_names:
            if name.lower() in col_clean:
                return col
    return None

# Örnek kullanım:
arac_col = get_column(df, ['araç no', 'vehicle number', 'tram_id'])
# Returns first matching column

Best practice: Sabit kolon adları kullan (Excel template)
```

---

### Q: "Yeni proje eklemek için ne yapmalıyım?"
A:
```
1. Excel dosyaları hazırla:
   ├─ data/{project}/Veriler.xlsx (Sayfa2 with tram list)
   ├─ data/{project}/Güncel*.xlsx (Spare parts)
   └─ logs/{project}/ariza_listesi/Ariza_Listesi_{PROJECT}.xlsx

2. Veritabanını sync et:
   └─ python sync_fracas_data.py  # or use app UI

3. Code changes: NONE NEEDED
   - Dynamic project detection via session
   - File paths auto-adjust per project

4. Test:
   └─ Visit dashboard, select new project from dropdown
```

---

### Q: "Performance optimization? Nereyi optimize edemeliyim?"
A:
```
Top 3 bottlenecks (CMSv1.1):

1. ❌ /fracas dashboard (100-300ms)
   Solution: Add database indexes (READY_TO_APPLY_CODE.md)
   
2. ❌ Equipment query (no index on project_code)
   Solution: Index equipment(project_code, status)
   
3. ❌ Failure filtering (N+1 queries)
   Solution: eager loading with joinedload()

See: DATABASE_ARCHITECTURE.md "Query Performance Tuning"
See: OPTIMIZATION_PRIORITIES.md for implementation plan
```

---

## 📈 VERI BOYUTLARI ve TIMING

```
┌──────────────────────┬──────────┬─────────────┐
│ Operation            │ Records  │ Time (ms)   │
├──────────────────────┼──────────┼─────────────┤
│ List equipment       │ 25-150   │ 10-50ms     │
│ Load ariza_listesi   │ 23-50    │ 100-300ms   │
│ Get failures by equip│ 1-10     │ 50-100ms    │
│ Calculate MTTR       │ 50+      │ 200-500ms   │
│ Parts cache (cached) │ 500+     │ 10ms        │
│ Parts cache (load)   │ 500+     │ 100-200ms   │
└──────────────────────┴──────────┴─────────────┘

Database size: ~10 MB (SQLite)
Session cache: ~500 KB (parts cache)
```

---

## 🚨 COMMON ISSUES & SOLUTIONS

### Issue 1: "Arıza görünmüyor"
```
Troubleshoot:
1. File exist? 
   └─ logs/{project}/ariza_listesi/Ariza_Listesi_*.xlsx
2. Sheet name correct? 
   └─ "Ariza Listesi" (case sensitive)
3. Header row? 
   └─ Row 3 (header parameter = 3)
4. Check logs: 
   └─ logger.error in routes/fracas.py:load_ariza_listesi_data()

Solution:
├─ Verify Excel file path matches project name
├─ Check sheet tabs in Excel
└─ Run: python -c "import pandas as pd; df = pd.read_excel(..., header=3); print(df.columns)"
```

---

### Issue 2: "Proje değiş
tirlirken veri değişmiyor"
```
Cause: Cache not updated

Solution:
├─ Clear session: del session['current_project']
├─ Force reload: F5 (browser)
├─ Restart app: Ctrl+C + Run again
└─ Check: session['current_project'] in browser DevTools

Code location: app.py:250-280 (handle_project_selection)
```

---

### Issue 3: "Yedek parça listesi boş"
```
Cause: Güncel*.xlsx file missing or misnamed

Solution:
├─ Check file: data/{project}/Güncel*.xlsx exists?
├─ Check function: app.py:load_parts_cache()
├─ Check cache: 
    if 'belgrad' in _parts_cache:
        print(_parts_cache['belgrad'])
└─ Reset app: Restart Flask server
```

---

## 📚 DOKUMENTASYON REFERANSLARI

```
Detaylı veri akışı:
  └─ DATA_SOURCES_MAPPING.md (20+ Excel files breakdown)

Database şeması:
  └─ DATABASE_ARCHITECTURE.md (ER diagram + relationships)

Performance tuning:
  └─ OPTIMIZATION_PRIORITIES.md (indexing, caching, queries)

Sorun giderme:
  └─ REFACTORING_GUIDE.md (code issues documented)

Kod örnekleri:
  └─ READY_TO_APPLY_CODE.md (copy-paste optimization code)
```

---

**Sürüm**: CMSv1.1  
**Tarih**: 28 Mart 2026  
**Hazırlayan**: GitHub Copilot  
**Status**: ✅ Stable | ⚠️ Indexing önerilir
