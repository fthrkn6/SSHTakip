#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FRACAS ANALİZ SAYFASI - VERİ KAYNAKLARI (Özet)
"""

print("\n" + "="*120)
print("FRACAS ANALİZ SAYFASI - TÜM VERİLERİN KAYNAKLARI")
print("="*120 + "\n")

data = [
    ["GRAFİK/TABLO", "AÇIKLAMA", "KOLON KAYNAĞI", "FORMÜL/KOD", "SONUÇ (23 arıza)"],
    ["-"*25, "-"*35, "-"*25, "-"*35, "-"*20],
    
    # KPI Kartları
    ["TOPLAM ARIZA (KPI)", "Toplam arıza sayısı", "—", "len(df)", "23"],
    ["ARAÇ SAYISI (KPI)", "Farklı araç ID'si", "Araç No", "df['Araç No'].nunique()", "13"],
    ["MODÜL SAYISI (KPI)", "Farklı modül tipi", "Araç Modül", "df['Araç Modül'].nunique()", "5"],
    ["TEDARİKÇİ (KPI)", "Farklı supplier", "Tedarikçi", "df['Tedarikçi'].nunique()", "10"],
    ["GARANTI KAYDI (KPI)", "Garanti kapsamı", "Garanti Kapsamı", "df[...].contains('evet')", "?"],
    
    ["-"*25, "-"*35, "-"*25, "-"*35, "-"*20],
    
    # RAMS Metrikleri
    ["MTBF (RAMS)", "Arızalar arası ortalama", "Kilometre + Araç No", "KM aralığı / arıza sayısı", "1043 dakika"],
    ["MTTR (RAMS)", "Ortalama tamir süresi", "MTTR (dk)", "df['MTTR (dk)'].mean()", "52.3 dakika"],
    ["MDT (RAMS)", "Ortalama duruş süresi", "MTTR + bekleme", "MTTR + MWT", "52.3 dakika"],
    ["AVAILABILITY (RAMS)", "Kullanılabilirlik %", "MTBF + MTTR", "(MTBF/(MTBF+MTTR))*100", "95.24%"],
    ["RELIABILITY (RAMS)", "Güvenilirlik %", "—", "Varsayılan", "95.0%"],
    
    ["-"*25, "-"*35, "-"*25, "-"*35, "-"*20],
    
    # Pareto Analizi
    ["PARETO MOD. GRAF.", "Araç modülü dağılımı", "Araç Modül", "value_counts() → Bar+Line", "SB:8, T:5, SA:4..."],
    ["PARETO TEDARI. GR.", "Tedarikçi dağılımı", "Tedarikçi", "value_counts() → Bar+Line", "SKF:7, MİNEL:3..."],
    ["ARIZA SINIFI GRAF.", "Arıza sınıfı dağılımı", "Arıza Sınıfı", "value_counts() → Doughnut", "A:9, B:7, C:5, D:2"],
    ["ARIZA KONUMU GRAF.", "Alt sistem dağılımı", "Alt Sistem", "value_counts() → Pie", "Yağlama:6, ..."],
    
    ["-"*25, "-"*35, "-"*25, "-"*35, "-"*20],
    
    # Trend Analizi
    ["AYLIK TREND GRAF.", "Aylık arıza sayısı", "Tarih", "groupby(month) → Line", "2026-02: 23"],
    ["SAATLİK DAGILIM G.", "Saatlik arıza dağılımı", "Tarih", "groupby(hour) → Bar", "0:0, 1:0, 10:5..."],
    ["HAFTA GÜNÜ GRAF", "Haftanın günü dağılımı", "Tarih", "groupby(dayofweek) → Line", "Pazartesi:?, ..."],
    
    ["-"*25, "-"*35, "-"*25, "-"*35, "-"*20],
    
    # Tablo ve diğer
    ["TEDARİKÇİ TABLOS.", "Tedarikçi performansı", "Tedarikçi + MTTR", "groupby(Tedarikçi).mean()", "SKF:7|48.5..."],
    ["MALİYET ANALİZİ", "Maliyet bilgisi", "Garanti Kapsamı", "Garanti sayıları", "Veri yok"],
]

# Print table
for row in data:
    if row[0].startswith("-"):
        print("-"*120)
    else:
        print(f"{row[0]:<25} │ {row[1]:<35} │ {row[2]:<25} │ {row[3]:<35} │ {row[4]:<20}")

print("\n" + "="*120)
print("VERI KAYNAĞI: logs/belgrad/ariza_listesi/Ariza_Listesi_BELGRAD.xlsx")
print("    Sheet: 'Ariza Listesi', Header: Satır 4, Toplam veri: 23 arıza x 30 kolon")
print("="*120 + "\n")

print("""
VERI AKIŞI:

1. GET /fracas/  → Flask route
2. routes/fracas.py :: index() function
3. load_ariza_listesi_data()
   └─ logs/belgrad/ariza_listesi/Ariza_Listesi_BELGRAD.xlsx
   └─ pd.read_excel(sheet_name='Ariza Listesi', header=3)
4. DataFrame(23x30) ile 6 analiz yapılır:
   ├─ calculate_basic_stats()     → KPI (5 card)
   ├─ calculate_rams_metrics()    → RAMS (4 metrik)
   ├─ calculate_pareto_analysis() → 4 Chart (module/supplier/class/location)
   ├─ calculate_trend_analysis()  → 3 Chart (monthly/hourly/weekday)
   ├─ calculate_supplier_analysis() → Table (10+ suppliers)
   └─ calculate_cost_analysis()   → Cost info
5. render_template('fracas/index.html', data...)
6. Template Jinja2 loops → HTML + JavaScript
7. Chart.js render → Browser


TÜM VERİLERİN KAYNAKLARI:

┌─ EXCEL DOSYASI ─────────────────────────────────────────┐
│ logs/belgrad/ariza_listesi/Ariza_Listesi_BELGRAD.xlsx   │
│ ├─ Sheet: 'Ariza Listesi'                                │
│ ├─ Header satırı: 4. satır (header=3)                    │
│ ├─ Veri satırı: 23 adet kayıt                            │
│ └─ Kolon: 30 tanesinden kullanılan 13 kolon             │
│    ├─ Araç No (vehicle ID)                               │
│    ├─ Araç Modül (module: SB, T, SA, MC, M)             │
│    ├─ Kilometre (for MTBF calculation)                   │
│    ├─ Tarih (for trend analysis)                         │
│    ├─ Tedarikçi (supplier name)                          │
│    ├─ Arıza Sınıfı (failure class A,B,C,D)              │
│    ├─ Alt Sistem (location/subsystem)                    │
│    ├─ MTTR (dk) (repair time in minutes)                │
│    ├─ Garanti Kapsamı (warranty yes/no)                  │
│    └─ ... 21 more columns                                │
└─────────────────────────────────────────────────────────┘

KOLON MAPPING:

Açık Araç No             → 13 different vehicles
Açık Araç Modül          → 5 types (for Pareto 1)
Açık Kilometre           → MTBF calculation
Açık Tarih              → Trend (monthly/hourly/weekday)
Açık Tedarikçi          → Pareto 2 + Table
Açık Arıza Sınıfı       → Pareto 3 + KPI count
Açık Alt Sistem         → Pareto 4 (location)
Açık MTTR (dk)          → MTTR metric + Table mean
Açık Garanti Kapsamı    → KPI count + Cost


GRAFIK TARAFLARI (Database Query olması gibi):

SELECT count(*) FROM df                           → 23 (TOPLAM ARIZA)
SELECT count(DISTINCT `Araç No`) FROM df          → 13 (ARAÇ SAYISI)
SELECT count(DISTINCT `Araç Modül`) FROM df       → 5 (MODÜL SAYISI)
SELECT count(DISTINCT Tedarikçi) FROM df          → 10 (TEDARİKÇİ)
SELECT `Araç Modül`, count(*) FROM df GROUP BY 1  → [SB:8, T:5, ...] (PARETO MODÜL)
SELECT Tedarikçi, count(*) FROM df GROUP BY 1     → [SKF:7, MİNEL:3, ...] (PARETO TEDARI)
SELECT `Arıza Sınıfı`, count(*) FROM df GROUP BY 1 → [A:9, B:7, C:5, D:2] (ARIZA SINIFI)
SELECT `Alt Sistem`, count(*) FROM df GROUP BY 1  → [Yağlama:6, ...] (ARIZA KONUMU)
SELECT DATE(Tarih), count(*) FROM df GROUP BY 1   → [2026-02-10:?, ...] (AYLIK TREND)
SELECT HOUR(Tarih), count(*) FROM df GROUP BY 1   → [0:0, 1:0, ..., 10:5, ...] (SAATLİK)
SELECT Tedarikçi, AVG(`MTTR (dk)`) FROM df GROUP BY 1 → [SKF:48.5, ...] (TEDARI TABLO)


DOSYA/KOD YERLERİ:

Routes:
  ├─ routes/fracas.py              → index() @ line 195
  ├─ calculate_basic_stats()       @ line 253
  ├─ calculate_rams_metrics()      @ line 288
  ├─ calculate_pareto_analysis()   @ line 375
  ├─ calculate_trend_analysis()    @ line 440
  ├─ calculate_supplier_analysis() @ line 505
  └─ calculate_cost_analysis()     @ line 537

Template:
  └─ templates/fracas/index.html   → Chart.js loops

Utils:
  ├─ get_column()          @ line 236 → Kolon adı eşleştirme
  ├─ safe_numeric()        @ line 252 → Sayı konversiyon
  └─ load_ariza_listesi_data() @ line 111 → Excel okuma


HER KOLONU DİĞER ANALITIK TOOLLARDAN ÇEKMEDİĞİNİ BİLMEK:

1. Arıza Listesi dosyası lokal Excel dosyası
   ├─ Veritabanı değil
   ├─ API'dan çekilmiş değil
   ├─ FRACAS sisteminden senkronize değil
   └─ Manual Excel input

2. Dosya yolu sabitlenmiş:
   logs/{{ current_project }}/ariza_listesi/
   burada current_project = session['current_project']

3. Kolon adları sabit (Arıza Listesi template'inden):
   ├─ Araç No
   ├─ Araç Modül
   ├─ Kilometr
   ├─ Tarih
   ├─ Tedarikçi
   ├─ vb...

4. Tüm hesaplamalar local Python'da yapılıyor:
   ├─ Pandas DataFrame operations
   ├─ value_counts()
   ├─ groupby().mean()
   ├─ datetime parsing
   └─ Custom formulas (MTBF, Availability)

5. Cache yok:
   Sayfaya her zaman sayfa açıldığında dosya yeniden okunur
""")
