#!/usr/bin/env python3
"""Visual data source mapping"""

print(r"""
╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                          📊 PRÜJELERİN VERİ KAYNAKLARI (DATA SOURCES)                        ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│  🟢 AKTIF PROJELER (Active Projects)                                                        │
└──────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ BELGRAD (25 Tramvay)                            │
├─────────────────────────────────────────────────┤
│ ✅ Veriler.xlsx (Sayfa2)    → 25 araç ID        │
│ ✅ Equipment tablosu        → 25 kayıt          │
│ ✅ ServiceStatus tablosu    → 25 günlük durum   │
│   - İçinde status: Servis, Servis Dışı,        │
│                    İşletme Kaynaklı...         │
│ ✅ Bakım verileri           → Belgrad-Bakım.xlsx│
│ ✅ FRACAS raporu            → BEL25_FRACAS.xlsx│
│ ✅ HBR (Hata Bilgi Raporu)  → FR_010_R06...     │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ KAYSERI (11 Tramvay)                            │
├─────────────────────────────────────────────────┤
│ ✅ Veriler.xlsx (Sayfa2)    → 11 araç ID        │
│ ✅ Equipment tablosu        → 11 kayıt          │
│ ✅ ServiceStatus tablosu    → 11 günlük durum   │
│   - İçinde status: Servis, Servis Dışı,        │
│                    İşletme Kaynaklı...         │
│ ✅ Arıza listesi            → Ariza_Listesi.xlsx│
│ ✅ FRACAS raporu            → FRACAS.xlsx       │
│ ✅ HBR (Hata Bilgi Raporu)  → FR_010_R06...     │
└─────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│  🔴 HAZIRLIK AŞAMASINDA (Preparation Phase) - Veri yüklenmedi henüz                         │
└──────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ İASİ (25 Tramvay)                               │
├─────────────────────────────────────────────────┤
│ ❌ Veriler.xlsx (Sayfa2) mevcut? SADECE Excel   │
│ ❌ Equipment tablosu boş (0 kayıt)              │
│ ❌ ServiceStatus tablosu boş (0 kayıt)          │
│ ✅ FRACAS raporu mevcut → IASI_18-FR-549.xlsx   │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ TİMİŞOARA (40 Tramvay)                          │
├─────────────────────────────────────────────────┤
│ ❌ Equipment tablosu boş (0 kayıt)              │
│ ❌ ServiceStatus tablosu boş (0 kayıt)          │
│ ✅ FRACAS raporu mevcut → TIM16+24_FRACAS.xlsx  │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ KOCAELİ (10 Tramvay)                            │
├─────────────────────────────────────────────────┤
│ ❌ Equipment tablosu boş (0 kayıt)              │
│ ❌ ServiceStatus tablosu boş (0 kayıt)          │
│ ✅ FRACAS raporu mevcut → KOC10_FRACAS.xlsx     │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ GEBZE (25 Tramvay)                              │
├─────────────────────────────────────────────────┤
│ ❌ Equipment tablosu boş (0 kayıt)              │
│ ❌ ServiceStatus tablosu boş (0 kayıt)          │
│ ✅ FRACAS raporu mevcut → GDM7X4_FRACAS.xlsx    │
└─────────────────────────────────────────────────┘


╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                         📂 VERİ ÇEKME HİYERARŞİSİ (Data Hierarchy)                           ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝

┌─ ANA SAYFA (Dashboard) ────────────────────────────────────────────────────┐
│                                                                            │
│  1. Araçlar Listesi:                                                       │
│     └─ Equipment.query (project_code filter)                               │
│        └─ Veriler.xlsx Sayfa2 ile doğrulama                               │
│                                                                            │
│  2. Günlük Araç Durumu Kartları:                                           │
│     └─ ServiceStatus.query (tram_id, date, project_code)                   │
│        ├─ Status: "Servis" → Aktif                                        │
│        ├─ Status: "Servis Dışı" → Arıza                                   │
│        └─ Status: "İşletme Kaynaklı..." → İşletme                         │
│                                                                            │
│  3. İstatistikler:                                                         │
│     └─ Toplam Araç: Equipment count                                        │
│     └─ Serviste: ServiceStatus count (status='Servis')                     │
│     └─ Servis Dışı: ServiceStatus count (status='Servis Dışı')             │
│     └─ İşletme: ServiceStatus count (status='İşletme...')                  │
│     └─ Ort. Availability: (Serviste / Toplam) * 100                        │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

┌─ SERVİS DURUMU SAYFASI ────────────────────────────────────────────────────┐
│                                                                            │
│  Kartlar (Stat Cards):                                                     │
│  ├─ Toplam Araç    ← Equipment table (project_code)                        │
│  ├─ Serviste       ← ServiceStatus (status='Servis')                       │
│  ├─ Servis Dışı    ← ServiceStatus (status='Servis Dışı')                  │
│  ├─ İşletme        ← ServiceStatus (status='İşletme...')                   │
│  └─ Ort. Availability ← (Serviste/Toplam)*100                             │
│                                                                            │
│  Tablo (Table):                                                            │
│  └─ /servis/durumu/tablo endpoint                                          │
│     └─ Equipment.query + ServiceStatus.query (project_code)                │
│     └─ JSON döner: {stats: {...}, table_data: [...]}                      │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

┌─ ARAÇ DETAYLARI ───────────────────────────────────────────────────────────┐
│                                                                            │
│  Tram Bilgileri:                                                           │
│  ├─ Equipment table (parent_id=None)                                       │
│  │  └─ equipment_code, name, status (fallback)                             │
│  │                                                                         │
│  ├─ ServiceStatus (tram_id, today)                                         │
│  │  └─ status, system, subsystem                                           │
│  │                                                                         │
│  └─ Alt Sistemler:                                                         │
│     └─ Equipment (parent_id=tram_id)                                       │
│        └─ Şanzıman, Motor, vb.                                             │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                              📋 VERİ KAYNAGI DOSYA YERLEŞİMİ                                  ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝

data/
├── belgrad/
│   ├── Veriler.xlsx .......................... ✅ TRAMVAYLARİN LİSTESİ (25 tram)
│   ├── Belgrad-Bakım.xlsx ................... ✅ BAKIM VERİLERİ
│   ├── BEL25_FRACAS.xlsx ................... ✅ HATA RAPORLAMA (FRACAS)
│   ├── FR_010_R06_SSH HBR.xlsx ............. ✅ HATA BİLGİ RAPORU (HBR)
│   ├── GÜNCEL BELGRAD TRAMVAY*.XLSX ........ ℹ️  BACKUP DOSYA (794KB)
│   ├── km_data.json ........................ ℹ️  KM İSTATİSTİKLERİ
│   ├── maintenance.json .................... ℹ️  BAKIM JSON
│   └── service_status.json ................. ℹ️  DURUM JSON
│
├── kayseri/
│   ├── Veriler.xlsx ........................ ✅ TRAMVAYLARİN LİSTESİ (11 tram)
│   ├── Ariza_Listesi_KAYSERİ.xlsx ......... ✅ ARIZA LİSTESİ
│   ├── FR_010_R06_SSH HBR.xlsx ............ ✅ HATA BİLGİ RAPORU
│   └── GÜNCEL KAYSERİ*.XLSX .............. ℹ️  BACKUP DOSYA (899KB)
│
├── iasi/
│   ├── Veriler.xlsx ........................ ✅ TRAMVAYLARİN LİSTESİ (25 tram)
│   └── IASI_18-FR-549_FRACAS*.xlsx ........ ✅ HATA RAPORLAMA (1.9MB)
│
├── timisoara/
│   ├── Veriler.xlsx ........................ ✅ TRAMVAYLARİN LİSTESİ (40 tram)
│   └── TIM16+24_FRACAS*.xlsx .............. ✅ HATA RAPORLAMA (2.7MB)
│
├── kocaeli/
│   ├── Veriler.xlsx ........................ ✅ TRAMVAYLARİN LİSTESİ (10 tram)
│   └── KOC10_FRACAS*.xlsx ................. ✅ HATA RAPORLAMA (1.4MB)
│
└── gebze/
    ├── Veriler.xlsx ........................ ✅ TRAMVAYLARİN LİSTESİ (25 tram)
    └── GDM7X4_FRACAS*.xlsx ................ ✅ HATA RAPORLAMA (676KB)


╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                         💾 DATABASE-BACKED VERILER (Tablolar)                                ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝

┌─ Equipment Tablosu ─────────────────────────────────────────────────────────┐
│ Sütunlar: equipment_code, name, project_code, parent_id, status, ...        │
│ Toplam: 36 tram                                                              │
│ ├─ Belgrad: 25 (1531-1555)                                                  │
│ └─ Kayseri: 11 (3872-3882)                                                  │
│                                                                             │
│ Kullanım:                                                                   │
│ └─ equipment.query.filter_by(project_code=project).count()                 │
│    → Sayfada "Toplam Araç" sayısını göstermek için                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ ServiceStatus Tablosu ──────────────────────────────────────────────────────┐
│ Sütunlar: id, tram_id, date, status, project_code, system, subsystem, ...   │
│ Toplam: 36 kayıt (sadece bugün)                                              │
│ ├─ Belgrad: 25 (25 tram × 1 gün)                                            │
│ └─ Kayseri: 11 (11 tram × 1 gün)                                            │
│                                                                             │
│ Status değerleri:                                                           │
│ ├─ "Servis" ......................... AKTIF                                  │
│ ├─ "Servis Dışı" ................... ARIZA                                  │
│ └─ "İşletme Kaynaklı Servis Dışı" . İŞLETME                                 │
│                                                                             │
│ Kullanım:                                                                   │
│ ServiceStatus.query.filter_by(                                              │
│   tram_id=tram, date=today, project_code=project                            │
│ ).first()                                                                   │
│ → Herbir araçın günlük durumunu almak için                                  │
│                                                                             │
│ Unique Constraint: (tram_id, date, project_code)                            │
│ └─ Aynı araç, aynı gün, aynı proje = tek kayıt                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ Diğer Tablolar ────────────────────────────────────────────────────────────┐
│ WorkOrder      : 0 kayıt (benumuz zaten hazırlanmadı)                        │
│ Failure        : Veri var mı? 🤔 (ayrıntı lazım)                            │
│ RootCauseAnalysis : Veri var mı? 🤔 (ayrıntı lazım)                         │
└─────────────────────────────────────────────────────────────────────────────┘


╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                          🔐 VERİ İZOLASYONU (Project Isolation)                              ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝

✅ BELGRAD veriler:
   Equipment.query.filter_by(project_code='belgrad') → 25 kayıt
   ServiceStatus.query.filter_by(project_code='belgrad') → 25 kayıt
   Veriler.xlsx okuma: data/belgrad/Veriler.xlsx Sayfa2

✅ KAYSERI veriler:
   Equipment.query.filter_by(project_code='kayseri') → 11 kayıt
   ServiceStatus.query.filter_by(project_code='kayseri') → 11 kayıt
   Veriler.xlsx okuma: data/kayseri/Veriler.xlsx Sayfa2

❌ KARIŞTIRıMıZ YOK:
   Belgrad verisi Kayseri sayfasında çıkmıyor
   Kayseri verisi Belgrad sayfasında çıkmıyor
   Her proje kendi verisini kendi project_code'u ile çekiyor


╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                            📊 VERİ TOPLAM İSTATİSTİKLERİ                                    ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝

Proje              Tram  Excel  DB Equipment  ServiceStatus  Fracas    Durum
─────────────────────────────────────────────────────────────────────────────
BELGRAD             25    ✅      ✅  25          ✅  25       ✅    🟢 Aktif
KAYSERI             11    ✅      ✅  11          ✅  11       ✅    🟢 Aktif
İASİ                25    ✅      ❌   0          ❌   0       ✅    🔴 Yüklenmedi
TİMİŞOARA           40    ✅      ❌   0          ❌   0       ✅    🔴 Yüklenmedi
KOCAELİ             10    ✅      ❌   0          ❌   0       ✅    🔴 Yüklenmedi
GEBZE               25    ✅      ❌   0          ❌   0       ✅    🔴 Yüklenmedi
─────────────────────────────────────────────────────────────────────────────
TOPLAM             136    ✅      36          36          ✅

""")
