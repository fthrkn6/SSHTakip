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
🔄 DATA FLOW ÖZET:

1. Sayfaya git: GET /fracas/
2. routes/fracas.py :: index() çağrılır
3. load_ariza_listesi_data() 
   → logs/belgrad/ariza_listesi/Ariza_Listesi_BELGRAD.xlsx 
   → pd.read_excel(header=3)
4. DataFrame df ile aşağıdaki 6 işlemi yap:
   a) calculate_basic_stats(df)      → KPI kartları
   b) calculate_rams_metrics(df)     → RAMS metrikleri
   c) calculate_pareto_analysis(df)  → 4 Pareto grafiği
   d) calculate_trend_analysis(df)   → 3 Trend grafiği
   e) calculate_supplier_analysis(df) → Tedarikçi tablosu
   f) calculate_cost_analysis(df)    → Maliyet info
5. render_template('fracas/index.html', ...) ile template'e veri geç
6. HTML Template Jinja2 loops ile grafikler ve veriler render edilir
7. Chart.js JavaScript'i veri tarafından grafikler oluşturur
8. Browser'da gösterilir


📍 HER GRAFIK NEREDEN VERİ ÇEKIYOR:

KPI KARTLARI (5 tane):
  ├─ Toplam Arıza → len(df)
  ├─ Araç Sayısı → df['Araç No'].nunique()
  ├─ Modül Sayısı → df['Araç Modül'].nunique()
  ├─ Tedarikçi → df['Tedarikçi'].nunique()
  └─ Garanti → df['Garanti Kapsamı'].value_counts()

RAMS METRİKLERİ (4 tane):
  ├─ MTBF → df['Kilometre'] hesaplaması
  ├─ MTTR → df['MTTR (dk)'].mean()
  ├─ Availability → (MTBF / MTBF+MTTR)*100
  └─ Reliability → 95% default

GRAFİKLER (6 tane):
  ├─ Pareto Modül → df['Araç Modül'].value_counts()
  ├─ Pareto Tedarikçi → df['Tedarikçi'].value_counts()
  ├─ Aylık Trend → df['Tarih'].groupby(month).size()
  ├─ Saatlik → df['Tarih'].dt.hour.value_counts()
  ├─ Arıza Sınıfı → df['Arıza Sınıfı'].value_counts()
  └─ Konumu → df['Alt Sistem'].value_counts()

TABLO:
  └─ Tedarikçi Performans → df.groupby('Tedarikçi')['MTTR (dk)'].mean()


⚙️ KOD YERLER (Değişiklik Yapılacaksa Burası):

1. Kolon adlarını değiştirmek:
   → routes/fracas.py :: get_column() fonksiyonunda possible_names listesi

2. Veri kaynağını değiştirmek:
   → routes/fracas.py :: load_ariza_listesi_data() veya load_fracas_data()

3. Grafikleri değişt:
   → templates/fracas/index.html :: JavaScript Chart.js seçenekleri

4. Hesaplama formülünü değiştirmek:
   → routes/fracas.py :: calculate_* fonksiyonları
""")
