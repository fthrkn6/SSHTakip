#!/usr/bin/env python3
"""Generate detailed data flow architecture and flowchart"""

print(r"""
╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                    🎯 MIMARI VERİ AKIŞI (ARCHITECTURAL DATA FLOW)                             ║
║                      Sayfalar → Veriler → Hesaplama → Gösterim                                ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝


██████████████████████████████████████████████████████████████████████████████████████████████████
█                    📊 SAYFA 1: ANA SAYFA (DASHBOARD) - /dashboard                            █
██████████████████████████████████████████████████████████████████████████████████████████████████

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1️⃣  ÇALIŞAN KULLANICI (LOGIN USER)                                                         │
│    └─ current_project = 'belgrad' (sessiyon'dan okunur)                                     │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2️⃣  VERİ KAYNAKÇALARI (DATA SOURCES)                                                       │
│    ├─ Tram/Araç Listesi:                                                                   │
│    │  └─ Equipment.query.filter_by(                                                        │
│    │     project_code=current_project,                                                    │
│    │     parent_id=None                                                                   │
│    │  )                                                                                     │
│    │  └─ SQL: SELECT * FROM equipment WHERE project_code='belgrad' AND parent_id IS NULL  │
│    │  └─ Döner: 25 araç (belgrad-1531 ... belgrad-1555)                                   │
│    │                                                                                       │
│    ├─ Günlük Durum Verisi:                                                                │
│    │  └─ ServiceStatus.query.filter_by(                                                   │
│    │     project_code=current_project,                                                    │
│    │     date=today  # "2026-02-20"                                                       │
│    │  )                                                                                     │
│    │  └─ SQL: SELECT * FROM service_status                                                │
│    │     WHERE project_code='belgrad' AND date='2026-02-20'                               │
│    │  └─ Döner: 25 kayıt, her birinde status (Servis, Servis Dışı, vb.)                   │
│    │                                                                                       │
│    └─ İstatistik Hesapla:                                                                 │
│       └─ for each equipment in equipment_list:                                             │
│          ├─ Find ServiceStatus for this equipment today                                    │
│          ├─ Parse status value:                                                            │
│          │  ├─ "Servis" → aktif_count ++                                                  │
│          │  ├─ "Servis Dışı" → servis_disi_count ++                                        │
│          │  └─ "İşletme Kaynaklı..." → isletme_count ++                                   │
│          └─ Result: {aktif: 9, ariza: 8, isletme: 8, toplam: 25}                          │
│                                                                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ 3️⃣  TEMPLATE'E GÖNDER (SEND TO TEMPLATE)                                                    │
│    ├─ equipments = [Equipment...]                                                          │
│    ├─ stats = {aktif: 9, servis_disi: 8, isletme: 8, toplam: 25, erisebilirlik: 36.0}    │
│    ├─ today_date = "2026-02-20"                                                            │
│    └─ current_project = "belgrad"                                                          │
│                                                                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ 4️⃣  HTML RENDERLE (RENDER HTML)                                                              │
│    ├─ Ana Sayfa Kartları:                                                                  │
│    │  ├─ Toplam Araç: {{ stats.toplam }} = 25                                             │
│    │  ├─ Serviste: {{ stats.aktif }} = 9   (Servis Durumu)                                │
│    │  ├─ Servis Dışı: {{ stats.servis_disi }} = 8   (Arıza)                               │
│    │  ├─ İşletme: {{ stats.isletme }} = 8   (İşletme Kaynaklı)                            │
│    │  └─ Ort. Kullanılabilirlik: {{ stats.erisebilirlik }}% = 36.0%                       │
│    │                                                                                       │
│    ├─ İstatistik Grafiği:                                                                 │
│    │  └─ Pie Chart / Bar Chart:                                                           │
│    │     ├─ Servis (Aktif): 9 (36%)                                                       │
│    │     ├─ Servis Dışı: 8 (32%)                                                          │
│    │     └─ İşletme: 8 (32%)                                                              │
│    │                                                                                       │
│    └─ Tabel (Araç Listesi):                                                                │
│       ├─ Başlık: Tram ID | Durum | Sistem | Alt Sistem                                    │
│       └─ Satırlar: Her araç için Equipment + ServiceStatus bilgisi                        │
│                                                                                            │
└─────────────────────────────────────────────────────────────────────────────────────────────┘


██████████████████████████████████████████████████████████████████████████████████████████████████
█                  📋 SAYFA 2: SERVİS DURUMU SAYFASI - /servis/durumu                         █
██████████████████████████████████████████████████████████████████████████████████████████████████

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1️⃣  SAYFA YÜKLENİŞİ (PAGE LOAD)                                                             │
│    ├─ Route: /servis/durumu                                                                │
│    ├─ Function: service_status_page()                                                      │
│    └─ Parametreler: request.args.get('project') = 'belgrad'                                │
│                                                                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2️⃣  BACKEND HESAPLA (BACKEND CALCULATION)                                                   │
│    ├─ get_tram_ids_from_veriler('belgrad')                                                │
│    │  └─ data/belgrad/Veriler.xlsx Sayfa2 okur                                            │
│    │  └─ 25 tram_id bulur: [1531, 1532, ..., 1555]                                       │
│    │                                                                                       │
│    ├─ equipment_list = Equipment.query.filter_by(project_code='belgrad'...)                │
│    │  └─ DB'den: belgrad-1531, belgrad-1532, ..., belgrad-1555 (25 kayıt)                │
│    │                                                                                       │
│    └─ İstatistik Hesapla (DetailedStatistics):                                            │
│       ├─ aktif_count = 0, servis_disi_count = 0, isletme_count = 0                       │
│       ├─ for each tram in equipment_list:                                                 │
│       │  ├─ ss = ServiceStatus.query.filter_by(                                          │
│       │  │    tram_id=tram.equipment_code,                                               │
│       │  │    date='2026-02-20',                                                          │
│       │  │    project_code='belgrad'                                                      │
│       │  │  )                                                                              │
│       │  │  └─ SQL: SELECT * FROM service_status                                         │
│       │  │     WHERE tram_id='belgrad-1531' AND date='2026-02-20'                        │
│       │  │     AND project_code='belgrad' LIMIT 1                                         │
│       │  │                                                                                 │
│       │  └─ if ss.status contains 'İşletme': isletme_count++                             │
│       │     elif ss.status contains 'Dışı': servis_disi_count++                           │
│       │     elif ss.status contains 'Servis': aktif_count++                               │
│       │                                                                                     │
│       └─ stats = {                                                                        │
│          'aktif': 9,                                                                      │
│          'servis_disi': 8,                                                                │
│          'isletme': 8,                                                                    │
│          'toplam': 25,                                                                    │
│          'availability': 36.0                                                             │
│          }                                                                                  │
│                                                                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ 3️⃣  TEMPLATE'E GÖNDER (TO TEMPLATE)                                                         │
│    └─ render_template('servis_durumu_enhanced.html',                                       │
│       equipments=equipment_list,                                                          │
│       stats=stats,                                                                        │
│       today_date='2026-02-20',                                                            │
│       current_project='belgrad'                                                           │
│    )                                                                                        │
│                                                                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ 4️⃣  SAYFA GÖSTERIM (PAGE DISPLAY)                                                           │
│    ├─ Sabit Kartlar (Static Cards):                                                       │
│    │  │  ← İlk yükleme sırasında 0 gösterilir                                             │
│    │  ├─ <div id="totalVehicles">0</div>                                                  │
│    │  ├─ <div id="operationalCount">0</div>                                               │
│    │  ├─ <div id="outofserviceCount">0</div>                                              │
│    │  ├─ <div id="maintenanceCount">0</div>                                               │
│    │  └─ <div id="avgAvailability">0%</div>                                               │
│    │                                                                                       │
│    └─ JavaScript Güncelle (JavaScript Update):                                            │
│       ├─ refreshTable() çalışır (sayfayüklenmesi sırasında)                              │
│       ├─ fetch('/servis/durumu/tablo')  ← AJAX çağrısı                                    │
│       │  └─ Endpoint: /servis/durumu/tablo                                                │
│       │  └─ Parametreler: project_code='belgrad'                                          │
│       │  └─ Response JSON:                                                                │
│       │     {                                                                              │
│       │        "stats": {                                                                 │
│       │           "operational": 9,                                                      │
│       │           "outofservice": 8,                                                      │
│       │           "maintenance": 8,                                                       │
│       │           "total": 25,                                                            │
│       │           "availability": 36.0                                                    │
│       │        },                                                                          │
│       │        "table_data": [...]                                                        │
│       │     }                                                                              │
│       │                                                                                     │
│       └─ Kartları Güncelle (Update Cards):                                                │
│          └─ document.getElementById('totalVehicles').innerHTML = 25                       │
│          └─ document.getElementById('operationalCount').innerHTML = 9                     │
│          └─ document.getElementById('outofserviceCount').innerHTML = 8                    │
│          └─ document.getElementById('maintenanceCount').innerHTML = 8                     │
│          └─ document.getElementById('avgAvailability').innerHTML = 36.0%                  │
│                                                                                            │
└─────────────────────────────────────────────────────────────────────────────────────────────┘


██████████████████████████████████████████████████████████████████████████████████████████████████
█              🏗️  SERVİS DURUMU TABLOSU ENDPOİNTİ - /servis/durumu/tablo                    █
██████████████████████████████████████████████████████████████████████████████████████████████████

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1️⃣  İstek GReceive (REQUEST)                                                                │
│    ├─ Yöntem: GET                                                                          │
│    ├─ URL: /servis/durumu/tablo?project_code=belgrad                                      │
│    └─ Header: Authorization (JWT token ile)                                                │
│                                                                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2️⃣  PROJE KOD AYIKLA (EXTRACT PROJECT CODE)                                                 │
│    ├─ current_project = get_user_project() → 'belgrad'                                    │
│    │  Veya: project_code = request.args.get('project_code') → 'belgrad'                  │
│    └─ Doğrulama: Sadece authorized projects                                               │
│                                                                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ 3️⃣  VERİ ALA (FETCH DATA)                                                                  │
│    ├─ Araç Listesi:                                                                       │
│    │  └─ tram_ids = get_tram_ids_from_veriler('belgrad')                                 │
│    │     └─ data/belgrad/Veriler.xlsx Sayfa2'den oku                                     │
│    │     └─ 25 tram ID bulur                                                              │
│    │                                                                                       │
│    ├─ Equipment Verileri:                                                                 │
│    │  └─ equipment_list = Equipment.query.filter_by(project_code='belgrad')              │
│    │     └─ WHERE project_code='belgrad'                                                 │
│    │     └─ 25 kayıt döner                                                                │
│    │                                                                                       │
│    └─ GünGPlük Durum Verileri:                                                             │
│       └─ for each equipment:                                                              │
│          ├─ ss = ServiceStatus.query.filter_by(                                          │
│          │    tram_id=equipment.equipment_code,                                          │
│          │    date=today,                                                                │
│          │    project_code='belgrad'                                                      │
│          │  )                                                                              │
│          │  └─ Status: "Servis" / "Servis Dışı" / "İşletme Kaynaklı..."                 │
│          └─ sistem/alt_sistem bilgisi                                                      │
│                                                                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ 4️⃣  İSTATİSTİK HESAPLA (CALCULATE STATS)                                                   │
│    └─ for each equipment:                                                                 │
│       ├─ if status contains 'İşletme' → isletme++                                         │
│       ├─ elif status contains 'Dışı' → ariza++                                            │
│       └─ else → aktif++                                                                    │
│       └─ Result: {operational: 9, outofservice: 8, maintenance: 8, total: 25, ...}       │
│                                                                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ 5️⃣  TABEL VERİSİ HAZIRLA (PREPARE TABLE DATA)                                              │
│    └─ for each equipment in equipment_list:                                               │
│       ├─ table_row = {                                                                    │
│       │    tram_id: "belgrad-1531",                                                      │
│       │    name: "Tramvay 1531",                                                          │
│       │    status_display: "Aktif" / "Arıza" / "İşletme",                                │
│       │    sistem: "Ana Sistem",                                                          │
│       │    alt_sistem: "Mekanik",                                                         │
│       │    updated_at: "2026-02-20 10:30:00"                                             │
│       │  }                                                                                  │
│       └─ table_data.append(table_row)                                                     │
│                                                                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ 6️⃣  JSON YANIT GÖNDER (SEND JSON RESPONSE)                                                 │
│    └─ return jsonify({                                                                     │
│       "stats": {                                                                          │
│          "operational": 9,       ← Aktif araç sayısı                                      │
│          "outofservice": 8,      ← Servis dışı araç sayısı                                │
│          "maintenance": 8,       ← İşletme kaynaklı sayısı                                │
│          "total": 25,            ← Toplam araç sayısı                                     │
│          "availability": 36.0    ← %Kullanılabilirlik                                    │
│       },                                                                                    │
│       "table_data": [...]        ← Tablo satırları                                        │
│    })                                                                                       │
│                                                                                            │
└─────────────────────────────────────────────────────────────────────────────────────────────┘


██████████████████████████████████████████████████████████████████████████████████████████████████
█                        🔍 VERİ AKIŞI ÖZET (DATA FLOW SUMMARY)                              █
██████████████████████████████████████████████████████████████████████████████████████████████████

┌─ EXCEL DOSYA OKUMA ──────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│  FAİL: data/belgrad/Veriler.xlsx (Sayfa2)                                              │
│  ├─ Tram ID listesi: [1531, 1532, 1533, ..., 1555]                                    │
│  ├─ Format: Excel dosyası, Sayfa2 sayfası, tram_id sütunu                             │
│  ├─ Kullanım: Araçların kesin listesi (source of truth)                                │
│  └─ Okuma: get_tram_ids_from_veriler('belgrad') function                               │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─ DATABASE TABLOSU ───────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│  Equipment Tablosu (Araç Envanteri):                                                    │
│  ├─ Kolonlar: equipment_code, name, project_code, parent_id, status, ...              │
│  ├─ Filtre: WHERE project_code='belgrad' AND parent_id IS NULL                        │
│  ├─ Sonuç: 25 araç (Belgrad)                                                            │
│  ├─ Amaç: Araç listesi, sistem hiyerarşisi                                            │
│  └─ SQL Örneği:                                                                        │
│     SELECT * FROM equipment                                                            │
│     WHERE project_code='belgrad' AND parent_id IS NULL                                 │
│                                                                                         │
│  ServiceStatus Tablosu (Günlük Durum Kaydı):                                            │
│  ├─ Kolonlar: id, tram_id, date, status, project_code, sistem, alt_sistem             │
│  ├─ Filtre: WHERE tram_id='belgrad-1531' AND date='2026-02-20'                        │
│  │          AND project_code='belgrad'                                                  │
│  ├─ Sonuç: 1 kayıt (her araç, her gün için maksimum 1 kayıt)                           │
│  ├─ Amaç: Günlük durum kaydı (Servis, Arıza, İşletme)                                 │
│  ├─ Unique Constraint: (tram_id, date, project_code)                                   │
│  └─ SQL Örneği:                                                                        │
│     SELECT * FROM service_status                                                       │
│     WHERE tram_id='belgrad-1531' AND date='2026-02-20'                                 │
│     AND project_code='belgrad' LIMIT 1                                                 │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─ HESAPLAMA MANTIK ───────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│  İstatistik Hesaplama Algoritması:                                                      │
│                                                                                         │
│  aktif_count = 0                                                                       │
│  ariza_count = 0                                                                       │
│  isletme_count = 0                                                                     │
│                                                                                         │
│  for each equipment in equipment_list:                                                 │
│      status = ServiceStatus.query(tram_id, date, project_code).status                 │
│      if status contains 'İşletme':          # "İşletme Kaynaklı Servis Dışı"          │
│          isletme_count += 1                                                             │
│      elif status contains 'Dışı':           # "Servis Dışı"                            │
│          ariza_count += 1                                                               │
│      else:                                  # "Servis"                                  │
│          aktif_count += 1                                                               │
│                                                                                         │
│  stats = {                                                                              │
│      'aktif': aktif_count,                   # 9                                       │
│      'servis_disi': ariza_count,             # 8                                       │
│      'isletme': isletme_count,               # 8                                       │
│      'toplam': equipment_list.count(),       # 25                                      │
│      'availability': (aktif/toplam) * 100    # 36.0%                                   │
│  }                                                                                      │
│                                                                                         │
│  NOT: İçerik taraması yapılır çünkü yanlış .lower() Unicode çekmeyebilir              │
│       'İşletme' in status                    # ← Doğru                                 │
│       status.lower()                         # ← Yanlış (Unicode)                     │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─ TEMPLATE GÖSTERIM ──────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│  Jinja2 Şablonu (servis_durumu_enhanced.html):                                          │
│  ├─ {{eşitlendirmeler}} → stats dict değerlerinden                                     │
│  ├─ {{equipments}} → equipment_list'ten                                                 │
│  ├─ {{today_date}} → İşlenmiş tarih                                                    │
│  └─ {{current_project}} → Proje kodu                                                    │
│                                                                                         │
│  JavaScript Güncellemeler (AJAX):                                                       │
│  ├─ refreshTable() → sayfayüklenmesi sırasında çalışır                                 │
│  ├─ fetch('/servis/durumu/tablo') → Endpoint'e istek                                   │
│  ├─ response.json() → JSON ayrıştır                                                     │
│  ├─ document.getElementById(...).innerHTML → Kartları güncelle                         │
│  └─ dataTable.clear().rows.add(...).draw() → Tabloyu güncelle                         │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘


╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                               📌 PROJE İZOLASYONU (PROJECT ISOLATION)                         ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝

Herbir sayfada project_code filtresi kullanılır:

┌─ BELGRAD (current_project = 'belgrad') ──────────────┐
│                                                       │
│  Equipment:                                           │
│  SELECT * FROM equipment                            │
│  WHERE project_code='belgrad' AND parent_id IS NULL │
│  └─ 25 araç: belgrad-1531 ... belgrad-1555          │
│                                                       │
│  ServiceStatus:                                       │
│  SELECT * FROM service_status                       │
│  WHERE project_code='belgrad' AND date='2026-02-20' │
│  └─ 25 kayıt (her araç için 1 kayıt)               │
│                                                       │
│  Excel:                                              │
│  data/belgrad/Veriler.xlsx Sayfa2                   │
│  └─ 25 tram_id                                       │
│                                                       │
└───────────────────────────────────────────────────────┘

┌─ KAYSERI (current_project = 'kayseri') ──────────────┐
│                                                       │
│  Equipment:                                           │
│  SELECT * FROM equipment                            │
│  WHERE project_code='kayseri' AND parent_id IS NULL │
│  └─ 11 araç: kayseri-3872 ... kayseri-3882         │
│                                                       │
│  ServiceStatus:                                       │
│  SELECT * FROM service_status                       │
│  WHERE project_code='kayseri' AND date='2026-02-20' │
│  └─ 11 kayıt                                         │
│                                                       │
│  Excel:                                              │
│  data/kayseri/Veriler.xlsx Sayfa2                   │
│  └─ 11 tram_id                                       │
│                                                       │
└───────────────────────────────────────────────────────┘

✅ KARIŞTıRıLMAZ:
   Belgrad verisi sadece Belgrad'a ait user'a gösterilir
   Kayseri verisi sadece Kayseri'ye ait user'a gösterilir
   Her proje kendi verisini kendi project_code'u ile çeker


╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                              📂 TOPLAM PROJE SAYILARI (TOTALS)                               ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝

Proje             Araçlar  Equipment  ServiceStatus  Excel File             Durum
─────────────────────────────────────────────────────────────────────────────────────
BELGRAD              25       50         50          data/belgrad/V.xlsx      🟢 Aktif
KAYSERI              11       22         22          data/kayseri/V.xlsx      🟢 Aktif
İASİ                 25       25         25          data/iasi/V.xlsx         🟢 Aktif
TİMİŞOARA            40       80         40          data/timisoara/V.xlsx    🟢 Aktif
KOCAELİ              10       20         10          data/kocaeli/V.xlsx      🟢 Aktif
GEBZE                25       25         25          data/gebze/V.xlsx        🟢 Aktif
─────────────────────────────────────────────────────────────────────────────────────
TOPLAM              136      222        172          Tüm projeler            🟢 HAZIR

NOT: Equipment sayısı artmıştır çünkü proje kodları prefix'olarak eklendi
     (örn: belgrad-1531, kayseri-3872 vb.)

""")
