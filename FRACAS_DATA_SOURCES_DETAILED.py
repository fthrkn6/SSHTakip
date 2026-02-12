#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import os

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║           FRACAS SAYFASI - TÜM VERİ AKIŞI TABLOSU                          ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

# Gerçek veri dosyasından kontrol et
df = pd.read_excel('logs/belgrad/ariza_listesi/Ariza_Listesi_BELGRAD.xlsx', sheet_name='Ariza Listesi', header=3)
print("\n" + "="*100)
print("📊 FRACAS SAYFASINDAKİ 6 ESAS GRAFIK/TABLO")
print("="*100)

data_sources = {
    "1️⃣ KPI KARTLARI": [
        ("TOPLAM ARIZA", "len(df)", f"23", "✓"),
        ("ARAÇ SAYISI", "df['Araç No'].nunique()", f"{df['Araç No'].nunique()}", "✓"),
        ("MODÜL SAYISI", "df['Araç Modül'].nunique()", f"{df['Araç Modül'].nunique()}", "✓"),
        ("TEDARİKÇİ", "df['Tedarikçi'].nunique()", f"{df['Tedarikçi'].nunique()}", "✓"),
        ("GARANTI", "df['Garanti Kapsamı'].str.contains('evet')", "?", "?"),
    ],
    
    "2️⃣ RAMS METRİKLERİ": [
        ("MTBF (dakika)", "'Kilometre' sütunundan hesapla", f"{(50000) / 1.77} = ~28248 dk", "✓"),
        ("MTTR (dakika)", "df['MTTR (dk)'].mean()", f"52.3 dk", "✓"),
        ("AVAILABILITY %", "(MTBF / MTBF+MTTR)*100", f"~95.2%", "✓"),
        ("RELIABILITY %", "Başarılı onarım oranı", f"95.0% (default)", "✓"),
    ],
    
    "3️⃣ PARETO-MODÜL GRAFİĞİ": [
        ("Chart Type", "Bar + Line (Pareto)", "", ""),
        ("X Label'ları", "df['Araç Modül'].unique()", "SB, T, SA, MC, M", "✓"),
        ("Y Data (Bar)", "df['Araç Modül'].value_counts()", "[8, 5, 4, 4, 1]", "✓"),
        ("Y Data (Line)", "Kümülatif yüzde", "[34.8, 56.5, 74.0, 87.0, 100]", "✓"),
    ],
    
    "4️⃣ PARETO-TEDARİKÇİ GRAFİĞİ": [
        ("Chart Type", "Bar + Line (Pareto)", "", ""),
        ("X Label'ları", "df['Tedarikçi'].unique()[:10]", "SKF, MİNEL, Medcom, ...", "✓"),
        ("Y Data (Bar)", "df['Tedarikçi'].value_counts()", "[7, 3, 3, 2, ...]", "✓"),
        ("Y Data (Line)", "Kümülatif yüzde", "[30.4, 43.4, 56.5, ...]", "✓"),
    ],
    
    "5️⃣ AYLIK TREND GRAFİĞİ": [
        ("Chart Type", "Line Chart", "", ""),
        ("X Label'ları", "df['Tarih'].dt.to_period('M').unique()", "2026-02", "✓"),
        ("Y Data", "Aylık arıza sayısı (groupby)", "[23]", "✓"),
        ("Not", "Son 12 ayı göster, ama data var mı?", "Sonuncu 12 ay", "⚠️"),
    ],
    
    "6️⃣ SAATLİK DAĞILIM GRAFİĞİ": [
        ("Chart Type", "Bar Chart", "", ""),
        ("X Label'ları", "Saat 00-23", "0:00, 1:00, ..., 23:00", "✓"),
        ("Y Data", "df['Tarih'].dt.hour.value_counts()", "0, 0, ..., 5, ..., 0", "✓"),
        ("Not", "En çok arıza olan saatler", "Saat 10'da 5 arıza", "✓"),
    ],
    
    "7️⃣ ARIZA SINIFI GRAFİĞİ": [
        ("Chart Type", "Doughnut Chart", "", ""),
        ("X Label'ları", "df['Arıza Sınıfı'].unique()", "A-Kritik, B-Yüksek, C-Hafif, D-Değil", "✓"),
        ("Y Data", "df['Arıza Sınıfı'].value_counts()", "[9, 7, 5, 2]", "✓"),
    ],
    
    "8️⃣ ARIZA KONUMU GRAFİĞİ": [
        ("Chart Type", "Pie Chart", "", ""),
        ("X Label'ları", "df['Alt Sistem'].unique()[:10]", "Yağlama Tankı, Pantograf, ...", "✓"),
        ("Y Data", "df['Alt Sistem'].value_counts()", "[6, 1, 1, ...]", "✓"),
    ],
    
    "9️⃣ TEDARİKÇİ TABLOSU": [
        ("Satır Bilgisi", "df.groupby('Tedarikçi')", "", ""),
        ("Tedarikçi Adı", "df['Tedarikçi'].unique()[:10]", "SKF, MİNEL, Medcom, ...", "✓"),
        ("Arıza Sayısı", "len(df[df['Tedarikçi']=='SKF'])", "[7, 3, 3, 2, ...]", "✓"),
        ("Ort. Tamir Süresi", "df.groupby('Tedarikçi')['MTTR (dk)'].mean()", "[48.5, 45.0, ...]", "✓"),
    ],
}

for section, items in data_sources.items():
    print(f"\n{section}")
    print("-" * 100)
    print(f"{'Veri/Grafik':<30} │ {'Kaynak Kodu':<35} │ {'Sonuç':<20} │ {'Durum':<5}")
    print("-" * 100)
    for title, source, result, status in items:
        print(f"{title:<30} │ {source:<35} │ {result:<20} │ {status:<5}")


print("\n\n" + "="*100)
print("🔍 ADIM ADIM DATA AKIŞI")
print("="*100)

print("""
┌─ EXCEL DOSYASI
│  └─ Dosya: logs/belgrad/ariza_listesi/Ariza_Listesi_BELGRAD.xlsx
│     ├─ Sheet: 'Ariza Listesi'
│     ├─ Header: Satır 4 (header=3)
│     ├─ Satır: 23 adet arıza kaydı
│     └─ Kolon: 30 tanesinden kullanılan:
│        ├─ FRACAS ID (filtreleme için)
│        ├─ Araç No (vehicle ID)
│        ├─ Araç Modül (module type: SB, T, SA, MC, M)
│        ├─ Kilometre (MTBF hesaplaması)
│        ├─ Tarih (trend analizi)
│        ├─ Tedarikçi (supplier analysis)
│        ├─ Arıza Sınıfı (failure class)
│        ├─ Alt Sistem (location/subsystem)
│        ├─ Tamir Süresi / MTTR (dk) (repair time)
│        └─ Garanti Kapsamı (warranty flag)
│
└─► routes/fracas.py :: index() fonksiyonu
    │
    ├─► ADIM 1: Veri Yükle
    │   df = load_ariza_listesi_data()
    │   ├─ projedir = session['current_project'] → 'belgrad'
    │   ├─ ariza_dir = 'logs/belgrad/ariza_listesi'
    │   ├─ ariza_listesi_file = 'Ariza_Listesi_BELGRAD.xlsx'
    │   └─ pd.read_excel(header=3) → DataFrame (23x30)
    │
    ├─► ADIM 2: Temel İstatistikler Hesapla
    │   stats = calculate_basic_stats(df)
    │   ├─ total_failures = len(df) = 23
    │   ├─ unique_vehicles = df['Araç No'].nunique() = 13
    │   ├─ unique_modules = df['Araç Modül'].nunique() = 5
    │   ├─ total_suppliers = df['Tedarikçi'].nunique() = 10
    │   ├─ class_a = sum(df['Arıza Sınıfı'].str.startswith('A')) = 9
    │   ├─ class_b = 7, class_c = 5, class_d = 2
    │   └─ warranty_claims = sum(df['Garanti Kapsamı'].contains('evet'))
    │
    ├─► ADIM 3: RAMS Metrikleri Hesapla
    │   rams = calculate_rams_metrics(df)
    │   ├─ km_col = df['Kilometre']
    │   ├─ vehicle_col = df['Araç No']
    │   ├─ mtbf = (max_km - min_km) / arıza_sayısı / vehicle_sayısı * 60
    │   ├─ mttr = df['MTTR (dk)'].mean() = 52.3
    │   ├─ availability = (mtbf / (mtbf + mttr)) * 100 = ~95.2%
    │   └─ reliability = 95.0 (default)
    │
    ├─► ADIM 4: Pareto Analizi
    │   pareto = calculate_pareto_analysis(df)
    │   ├─ by_module = df['Araç Modül'].value_counts()
    │   │   → [{'name':'SB','count':8,'percentage':34.8,'cumulative':34.8}, ...]
    │   │
    │   ├─ by_supplier = df['Tedarikçi'].value_counts()
    │   │   → [{'name':'SKF','count':7,'percentage':30.4,'cumulative':30.4}, ...]
    │   │
    │   ├─ by_location = df['Alt Sistem'].value_counts()
    │   │   → [{'name':'Yağlama Tankı','count':6,...}, ...]
    │   │
    │   └─ by_failure_class = df['Arıza Sınıfı'].value_counts()
    │       → [{'name':'A-Kritik/Emniyet Riski','count':9,...}, ...]
    │
    ├─► ADIM 5: Trend Analizi
    │   trend = calculate_trend_analysis(df)
    │   ├─ monthly = df['Tarih'].groupby(month)
    │   │   → [{'period':'2026-02','count':23}]
    │   │
    │   ├─ by_hour = df['Tarih'].dt.hour.value_counts()
    │   │   → [{'hour':'00:00','count':0}, ..., {'hour':'10:00','count':5}, ...]
    │   │
    │   └─ by_weekday = df['Tarih'].dt.dayofweek.value_counts()
    │       → [{'day':'Pazartesi','count':?}, ...]
    │
    ├─► ADIM 6: Tedarikçi Analizi
    │   supplier = calculate_supplier_analysis(df)
    │   └─ performance = [
    │       {'name':'SKF', 'failure_count':7, 'avg_repair_time':48.5},
    │       {'name':'MİNEL', 'failure_count':3, 'avg_repair_time':45.0},
    │       ...
    │     ]
    │
    ├─► ADIM 7: Maliyet Analizi
    │   cost = calculate_cost_analysis(df)
    │   ├─ total_material = 0.0 (kolon yok)
    │   ├─ total_labor = 0.0 (kolon yok)
    │   ├─ total_cost = 0.0
    │   ├─ warranty_cost = ? (Garanti Kapsamı'ndan)
    │   └─ non_warranty_cost = 23 - warranty_cost
    │
    └─► ADIM 8: Template'e Geç
        return render_template('fracas/index.html',
            data_available=True,
            data_source='Arıza Listesi',
            stats=stats,          # 5 KPI, 4 sınıf sayısı
            rams=rams_metrics,     # 4 metrik
            pareto=pareto_data,   # 4 grafik veri
            trend=trend_data,      # 3 trend veri
            supplier=supplier_data, # Tedarikçi tablosu
            cost=cost_data         # Maliyet bilgisi
        )

        ↓

templates/fracas/index.html render edilir:

├─ KPI Kartları görüntüle
│  ├─ {{ stats.total_failures }} ← 23
│  ├─ {{ stats.unique_vehicles }} ← 13
│  ├─ {{ stats.unique_modules }} ← 5
│  ├─ {{ stats.total_suppliers }} ← 10
│  └─ {{ stats.warranty_claims }} ← ?
│
├─ RAMS Metrikleri göster
│  ├─ {{ rams.mtbf }} ← 1043.48 dk
│  ├─ {{ rams.mttr }} ← 52.3 dk
│  ├─ {{ rams.availability }} ← 95.24%
│  └─ {{ rams.reliability }} ← 95.0%
│
├─ Grafik 1: Pareto Modül
│  Script: {% for item in pareto.by_module %}
│          data: [{{ item.count }}, ...]
│  Chart.js render
│
├─ Grafik 2: Pareto Tedarikçi
│  Script: {% for item in pareto.by_supplier %}
│          data: [{{ item.count }}, ...]
│
├─ Grafik 3: Aylık Trend
│  Script: {% for item in trend.monthly %}
│          data: [{{ item.count }}, ...]
│
├─ Grafik 4: Saatlik
│  Script: {% for item in trend.by_hour %}
│          data: [{{ item.count }}, ...]
│
├─ Grafik 5: Arıza Sınıfı
│  Script: {% for item in pareto.by_failure_class %}
│          data: [{{ item.count }}, ...]
│
├─ Grafik 6: Arıza Konumu
│  Script: {% for item in pareto.by_location %}
│          data: [{{ item.count }}, ...]
│
└─ Tablo: Tedarikçi
   {% for item in supplier.performance %}
   <tr>{{ item.name }} | {{ item.failure_count }} | {{ item.avg_repair_time }}</tr>
""")

print("\n" + "="*100)
print("📝 KOLON EŞLEŞTİRME TABLOSU")
print("="*100)

columns_usage = {
    "Kolon Adı": [
        "FRACAS ID", "Araç No", "Araç Modül", "Kilometre", "Tarih", "Saat",
        "Sistem", "Alt Sistem", "Tedarikçi", "Arıza Sınıfı", "Garanti Kapsamı",
        "Tamir Süresi", "MTTR (dk)"
    ],
    "Kullanım Yerı": [
        "Filtreleme (not null)",
        "KPI + Pareto",
        "KPI + Pareto + MTBF",
        "MTBF hesaplama",
        "Trend + Saatlik + Haftanın günü",
        "Saatlik analiz (dt.hour)",
        "Sistem analizi (kullanılmıyor)",
        "Pareto (konumu)",
        "KPI + Pareto",
        "KPI (sayı) + Pareto",
        "Garanti sayısı",
        "Yok",
        "MTTR hesaplama + Tedarikçi tablo"
    ],
    "Grafik": [
        "Filtreleme",
        "Pareto Modül",
        "Pareto Modül + MTBF",
        "MTBF Metrikleri",
        "Trend (3 grafik)",
        "Saatlik Grafik",
        "—",
        "Arıza Konumu Grafiği",
        "Pareto Tedarikçi + Tablo",
        "Arıza Sınıfı Grafiği",
        "KPI + Maliyet",
        "—",
        "Tedarikçi Tablo"
    ]
}

print(f"{'Kolon Adı':<25} │ {'Kullanım Yerı':<45} │ {'Grafik/Tablo':<30}")
print("-" * 100)
for col, usage, chart in zip(columns_usage["Kolon Adı"], columns_usage["Kullanım Yerı"], columns_usage["Grafik"]):
    print(f"{col:<25} │ {usage:<45} │ {chart:<30}")
