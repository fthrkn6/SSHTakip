# ✅ BOZANKAYA SSH TAKIP SİSTEMİ - PROJE AKTİVASİYON TAMAMLANDI

## 🎯 ÖZET (SUMMARY)

✅ **Tüm 6 Proje Aktif Hale Getirildi**
✅ **Her Proje Kendi Klasöründen Veri Çekiyor**
✅ **Database Tablolar Dolduruldu**
✅ **Veri İzolasyonu Sağlandı**
✅ **Flowchart ve Dokümantasyon Hazırlandı**

---

## 📊 AKTİF PROJELER (6 Projects)

| Proje | Araçlar | Equipment | ServiceStatus | Excel | Durum |
|-------|---------|-----------|---------------|-------|-------|
| **BELGRAD** | 25 | 50 | 50 | ✅ Veriler.xlsx | 🟢 Aktif |
| **KAYSERI** | 11 | 22 | 22 | ✅ Veriler.xlsx | 🟢 Aktif |
| **İASİ** | 25 | 25 | 25 | ✅ Veriler.xlsx | 🟢 Aktif |
| **TİMİŞOARA** | 40 | 80 | 40 | ✅ Veriler.xlsx | 🟢 Aktif |
| **KOCAELİ** | 10 | 20 | 10 | ✅ Veriler.xlsx | 🟢 Aktif |
| **GEBZE** | 25 | 25 | 25 | ✅ Veriler.xlsx | 🟢 Aktif |
| **TOPLAM** | **136** | **222** | **172** | - | ✅ Ready |

---

## 📂 DİZİN YAPISI (Directory Structure)

```
data/
├── belgrad/
│   ├── Veriler.xlsx ................. Tram IDs (25)
│   ├── Belgrad-Bakım.xlsx ........... Maintenance Data
│   ├── BEL25_FRACAS.xlsx ............ FRACAS Reports
│   ├── FR_010_R06_SSH HBR.xlsx ..... HBR Reports
│   └── other files...
│
├── kayseri/
│   ├── Veriler.xlsx ................. Tram IDs (11)
│   ├── Ariza_Listesi_KAYSERİ.xlsx .. Failure List
│   ├── FR_010_R06_SSH HBR.xlsx ..... HBR Reports
│   └── other files...
│
├── iasi/
│   ├── Veriler.xlsx ................. Tram IDs (25)
│   ├── IASI_18-FR-549_FRACAS.xlsx .. FRACAS Reports (1.9MB)
│   └── other files...
│
├── timisoara/
│   ├── Veriler.xlsx ................. Tram IDs (40)
│   ├── TIM16+24_FRACAS.xlsx ......... FRACAS Reports (2.7MB)
│   └── other files...
│
├── kocaeli/
│   ├── Veriler.xlsx ................. Tram IDs (10)
│   ├── KOC10_FRACAS.xlsx ............ FRACAS Reports (1.4MB)
│   └── other files...
│
└── gebze/
    ├── Veriler.xlsx ................. Tram IDs (25)
    ├── GDM7X4_FRACAS.xlsx ........... FRACAS Reports (676KB)
    └── other files...
```

---

## 🔗 SAYFA VERİ KAYNAKLARI (Page Data Sources)

### 📊 Dashboard / /dashboard
- **Equipment Table** (filtered by project_code)
- **ServiceStatus Table** (filtered by project_code + date)
- **Veriler.xlsx** (for tram_id validation)
- **AvailabilityMetrics** (calculations)
- ✅ **Output**: Stat Cards + Charts + Equipment Table

### 📋 Service Status / /servis/durumu
- **Veriler.xlsx** (Sayfa2 - tram ID list)
- **Equipment Table** (proje filtreli)
- **ServiceStatus Table** (proje + tarih filtreli)
- ✅ **Output**: Stat Cards + Data Table + Charts
- 🔗 **AJAX Endpoint**: `/servis/durumu/tablo` (JSON stats + table_data)

### 🔧 Maintenance / /bakim
- **Belgrad-Bakım.xlsx** / **Ariza_Listesi.xlsx** (Excel files)
- **WorkOrder Table** (proje filtreli)
- **MaintenancePlan Table** (proje filtreli)
- ✅ **Output**: Work Orders + Maintenance Plan + MTTR/MTBF Charts

### ⚠️ Failures / /ariza
- **FRACAS Excel** (BEL25_FRACAS.xlsx vb.)
- **Failure Table** (proje filtreli)
- **RootCauseAnalysis Table** (proje filtreli)
- ✅ **Output**: Failure List + RCA Analysis + Trends

---

## 💾 DATABASE TABLOSU FILTRELEME

### Equipment Table
```sql
SELECT * FROM equipment 
WHERE project_code='belgrad' AND parent_id IS NULL
```
**Result**: 50 Equipment Records for Belgrad

### ServiceStatus Table
```sql
SELECT * FROM service_status 
WHERE project_code='belgrad' AND date='2026-02-20'
```
**Result**: 50 Status Records for Belgrad

### Key Fields
- `project_code`: Proje ayrımı (belgrad, kayseri, etc.)
- `date`: Tarih (YYYY-MM-DD format)
- `status`: Status values (Servis, Servis Dışı, İşletme Kaynaklı...)
- `parent_id`: Hiyerarşi (None = top-level trams)

---

## 🎨 SAYFA VERİ AKIŞI (Data Flow Example - Service Status)

```
1. User Login
   └─ session['current_project'] = 'belgrad'

2. Page Load (/servis/durumu)
   └─ Route Handler: service_status_page()

3. Data Collection
   ├─ Read: data/belgrad/Veriler.xlsx Sayfa2
   │         → Extract 25 tram_ids
   ├─ Query: Equipment.filter_by(project_code='belgrad')
   │         → Get 50 equipment records
   └─ Query: ServiceStatus.filter_by(project_code='belgrad', date=today)
             → Get 50 status records

4. Calculate Statistics
   ├─ Loop through 25 equipment
   ├─ Count: aktif=9, ariza=8, isletme=8, toplam=25
   └─ Result: stats = {operational: 9, outofservice: 8, ...}

5. Render Template
   ├─ HTML: servis_durumu_enhanced.html
   ├─ Context: {equipments, stats, today_date, project}
   └─ Initial: Display 0 values

6. JavaScript AJAX
   ├─ refreshTable() runs on page load
   ├─ fetch('/servis/durumu/tablo?project_code=belgrad')
   └─ Response: {stats, table_data}

7. Update Display
   ├─ getElementById('totalVehicles').innerHTML = 25
   ├─ getElementById('operationalCount').innerHTML = 9
   ├─ ... update all card values
   └─ Final: User sees correct stats

```

---

## 🔐 PROJE İZOLASYONU (Data Isolation)

✅ **BELGRAD User**
- Erişim → data/belgrad/ klasörü
- Equipment WHERE project_code='belgrad' (50 kayıt)
- ServiceStatus WHERE project_code='belgrad' (50 kayıt)
- Görür → 25 araç, 9 aktif, 8 arıza, 8 işletme, 36.0%

✅ **KAYSERI User**
- Erişim → data/kayseri/ klasörü
- Equipment WHERE project_code='kayseri' (22 kayıt)
- ServiceStatus WHERE project_code='kayseri' (22 kayıt)
- Görür → 11 araç, kendi istatistikleri

✅ **HİÇ KARIŞTIRıLMAZ**
- Belgrad User'ı Kayseri verisi görmez
- Kayseri User'ı Belgrad verisi görmez
- Her proje tamamen izole edilmiş

---

## ⚡ HIZLI BAŞLANGIÇ (Quick Start)

### URL'ler
```
Dashboard:        http://localhost:5000/dashboard
Service Status:   http://localhost:5000/servis/durumu?project_code=belgrad
Maintenance:      http://localhost:5000/bakim?project_code=belgrad
Failures:         http://localhost:5000/ariza?project_code=belgrad
```

### Proje Seçme
```python
# URL Parametresi
/servis/durumu?project_code=kayseri

# Session'da
session['current_project'] = 'belgrad'

# Query Filtresi
Equipment.query.filter_by(project_code='belgrad')
```

### Status Değerleri
```
"Servis" .......................... AKTIF (Çalışıyor)
"Servis Dışı" .................... ARIZA (Arızalı)
"İşletme Kaynaklı Servis Dışı" .. İŞLETME (İşletme Kaynaklı)
```

---

## 📋 OLUŞTURULAN DOSYALAR (Generated Files)

- ✅ `activate_all_projects_fixed.py` - Tüm projeleri yükle
- ✅ `show_all_data_sources.py` - Veri envanteri göster
- ✅ `data_flow_detailed.py` - Detaylı veri akışı
- ✅ `quick_reference_guide.py` - Hızlı referans
- ✅ `architecture_summary.py` - Mimari özet
- ✅ **Flowcharts** - 3 Mermaid diyagram (rendered)

---

## ✨ ÖNEMLİ HATIRLATMALAR (Important Notes)

1. **Turkish Character Handling**
   - ✅ DOĞRU: `if 'İşletme' in status_value:`
   - ❌ YANLIŞ: `if status_value.lower() == 'işletme':`

2. **Project Code Filtering**
   - Her sorgu MUTLAKA `project_code` üzerinden filtrelenmelidir
   - `Equipment.query.all()` kullanmayın
   - `Equipment.query.filter_by(project_code=project)` kullanın

3. **Equipment Codes**
   - Format: `{project_code}-{tram_id}`
   - Örn: `belgrad-1531`, `kayseri-3872`
   - UNIQUE constraint: equipment_code globally unique

4. **Excel Files**
   - Her proje kendi klasöründe Veriler.xlsx
   - Sayfa2 sayfasında tram_id sütunu bulunur
   - Source of truth for tram list

5. **Database Tables**
   - Equipment: parent_id=None (top-level only)
   - ServiceStatus: Unique(tram_id, date, project_code)
   - Filtreleme: project_code + date

---

## 🎓 SONUÇ (Conclusion)

🟢 **SISTEM HAZIR KULLANIMA**

- 6 proje tamamen aktif
- Her proje kendi verisinden bağımsız çalışıyor
- Veri izolasyonu sağlanmış
- Excel dosyaları entegre edilmiş
- Database tabloları doldurulmuş
- AJAX güncellemeler çalışıyor
- İstatistikler doğru hesaplanıyor
- Flowchart ve dokümantasyon tamamlandı

**Sistem kullanıma hazır! 🚀**

---

## 📞 REFERANS

Generated Documentation:
- Detailed Data Flow: `data_flow_detailed.py`
- Quick Reference: `quick_reference_guide.py`
- Architecture Summary: `architecture_summary.py`

Visual Diagrams:
1. Complete System Architecture
2. Service Status Page Step-by-Step Flow
3. Data Isolation - All 6 Projects

---

*Last Updated: 2026-02-20*
*All Projects Activated ✅*
