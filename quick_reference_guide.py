#!/usr/bin/env python3
"""Quick Reference: Page Data Sources"""

reference = r"""
╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                          ⚡ HIZLI REFERANS - SAYFA VERİ KAYNAKLARI                           ║
╚════════════════════════════════════════════════════════════════════════════════════════════════╝

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 📊 ANA SAYFA (DASHBOARD) - /dashboard                                                      ┃
├────────────────────────────────────────────────────────────────────────────────────────────┤
┃ Hangi Veri Çekiliyor?                       Nerden?                      Nasıl Filtreleniyor?┃
├────────────────────────────────────────────────────────────────────────────────────────────┤
┃ Araç Listesi (25 tram)                      Equipment Table              project_code='belgrad'
┃ Günlük Durum (Serviste, Arıza, İşletme)   ServiceStatus Table          date='2026-02-20'
┃ İstatistikler (Tekme, %, Grafik)          Hesaplama (Backend)           Loop & Count
┃ Tram IDs Doğrulaması                       Veriler.xlsx (Sayfa2)        Belgrad klasörü
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ 🔗 Backend Fonksiyon: dashboard_page()                                                      ┃
┃ 📁 Template: dashboard.html                                                                 ┃
┃ 📊 Output: Stat Cards + Grafikler + Tablo                                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 📋 SERVİS DURUMU SAYFASI - /servis/durumu                                                  ┃
├────────────────────────────────────────────────────────────────────────────────────────────┤
┃ Hangi Veri Çekiliyor?                       Nerden?                      Nasıl Filtreleniyor?┃
├────────────────────────────────────────────────────────────────────────────────────────────┤
┃ Araç Listesi (25 tram)                      Equipment Table              project_code filter
┃ Günlük Durum Kayıtları                      ServiceStatus Table          date + project filter
┃ Tram İD'leri                                Veriler.xlsx Sayfa2          data/belgrad/ klasörü
┃ İstatistikler                               Backend Hesaplama            Status Sayımı
┃                                                                                              │
┃ STATUS MAPPING:                                                                             ┃
┃   "Servis" ........................... Aktif ........................... 9                  ┃
┃   "Servis Dışı" ..................... Arıza ........................... 8                  ┃
┃   "İşletme Kaynaklı Servis Dışı" .... İşletme ........................ 8                  ┃
┃   TOPLAM ............................ 25 | Availability ............... 36.0%             ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ 🔗 Backend Fonksiyonları:                                                                  ┃
┃    - service_status_page() → HTML render (initial 0 values)                               ┃
┃    - service_status_table() → JSON API endpoint                                           ┃
┃ 📁 Template: servis_durumu_enhanced.html                                                   ┃
┃ ⚡ JavaScript: refreshTable() + AJAX fetch()                                               ┃
┃ 📊 Output: Stat Cards + Table + Charts (JavaScript güncellemesi ile)                       ┃
┃                                                                                              │
┃ AJAX ENDPOINT: /servis/durumu/tablo?project_code=belgrad                                  ┃
┃   └─ Response: {                                                                           ┃
┃       "stats": {                                                                           ┃
┃         "operational": 9,                                                                  ┃
┃         "outofservice": 8,                                                                 ┃
┃         "maintenance": 8,                                                                  ┃
┃         "total": 25,                                                                       ┃
┃         "availability": 36.0                                                               ┃
┃       },                                                                                    ┃
┃       "table_data": [...equipment rows...]                                                 ┃
┃     }                                                                                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🔧 BAKIM SAYFASI - /bakim                                                                  ┃
├────────────────────────────────────────────────────────────────────────────────────────────┤
┃ Hangi Veri Çekiliyor?                       Nerden?                      Nasıl Filtreleniyor?┃
├────────────────────────────────────────────────────────────────────────────────────────────┤
┃ Araçlar (belgrad: 25)                       Equipment Table              project_code filter
┃ Bakım İş Emirleri                           WorkOrder Table              project_code filter
┃ Bakım Planı                                 MaintenancePlan Table        project_code filter
┃ MTTR İstatistikleri                         Hesaplama                    WorkOrder analizi
┃ MTBF İstatistikleri                         Hesaplama                    Downtime analizi
┃ Bakım Grafiği Verileri                      Excel & Database             Belgrad-Bakım.xlsx
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ 🔗 Backend Fonksiyon: maintenance_page()                                                   ┃
┃ 📁 Template: bakim.html                                                                    ┃
┃ 📊 Output: Work Orders + Maintenance Plan + MTTR/MTBF Grafikleri                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ⚠️ ARIZA SAYFASI - /ariza                                                                   ┃
├────────────────────────────────────────────────────────────────────────────────────────────┤
┃ Hangi Veri Çekiliyor?                       Nerden?                      Nasıl Filtreleniyor?┃
├────────────────────────────────────────────────────────────────────────────────────────────┤
┃ Arıza Listesi                               Failure Table                project_code filter
┃ Arıza Sınıflandırması                       Failure kategorileri         Tür/Sistem sort
┃ Root Cause Analysis                         RootCauseAnalysis Table      project_code filter
┃ Önerilen Çözümler                           RCA "solution" alanı         Filter + Display
┃ Arıza Trendi Grafiği                        Failure tablosu (date)       Time series
┃ Arıza Frekansı                              FRACAS Excel raporu          BEL25_FRACAS.xlsx
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ 🔗 Backend Fonksiyon: failure_page()                                                       ┃
┃ 📁 Template: ariza.html                                                                    ┃
┃ 📊 Output: Arıza Listesi + RCA + Trendler + FRACAS Analizi                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


🎯 ÖZET: HER SAYFA HANGİ KLASÖRÜ KULLANIR?
════════════════════════════════════════════════════════════════════════════════════════════════

BELGRADUser İçin:
├─ /dashboard → data/belgrad/ + Equipment (belgrad-1531...) + ServiceStatus (belgrad)
├─ /servis/durumu → data/belgrad/Veriler.xlsx + equipment + status (belgrad)
├─ /bakim → data/belgrad/Belgrad-Bakım.xlsx + WorkOrder (belgrad)
└─ /ariza → data/belgrad/BEL25_FRACAS.xlsx + Failure (belgrad) + RCA (belgrad)

KAYSERİ User İçin:
├─ /dashboard → data/kayseri/ + Equipment (kayseri-3872...) + ServiceStatus (kayseri)
├─ /servis/durumu → data/kayseri/Veriler.xlsx + equipment + status (kayseri)
├─ /bakim → data/kayseri/ + WorkOrder (kayseri)
└─ /ariza → data/kayseri/Ariza_Listesi_KAYSERİ.xlsx + Failure (kayseri) + RCA (kayseri)

...ve böyle her proje için devam ediyor


💡 ÖNEMLİ KURALLAR:
════════════════════════════════════════════════════════════════════════════════════════════════

1. HER SORGU project_code ÜZERINDE FİLTRELENMELİ
   ✅ DOĞRU:   Equipment.query.filter_by(project_code='belgrad')
   ❌ YANLIŞ:  Equipment.query.all()

2. EXCEL DOSYALARI PROJE KLASÖRÜNDE
   ✅ DOĞRU:   data/belgrad/Veriler.xlsx
   ❌ YANLIŞ:  data/Veriler.xlsx

3. STATUS METNI TARAMASI (Turkish Characters için)
   ✅ DOĞRU:   if 'İşletme' in status_value:
   ❌ YANLIŞ:  if status_value.lower() == 'işletme':

4. TÜZEL PERSONEL KOD FORMATI
   ✅ DOĞRU:   belgrad-1531, kayseri-3872
   ❌ YANLIŞ:  1531, 3872

5. AJAX UPDATE için JSON Response
   ✅ DOĞRU:   return jsonify({'stats': {...}, 'table_data': [...]})
   ❌ YANLIŞ:  return equipment_list (plain array)


📡 PROJE DEĞİŞTİR BİLİNMESİ:
════════════════════════════════════════════════════════════════════════════════════════════════

URL'de Parametre ile:
  /servis/durumu?project_code=kayseri → Kayseri verisi göster

Session'da:
  session['current_project'] = 'belgrad' → Tüm sayfalar belgrad verisi göster

get_user_project() Fonksiyonu:
  return 'belgrad'  # User'ın atanmış projesi


🎓 ÖRNEKLER (EXAMPLES):
════════════════════════════════════════════════════════════════════════════════════════════════

>>> # Equipment Sorgusu
>>> Equipment.query.filter_by(
...     project_code='belgrad',
...     parent_id=None
... ).all()
[Equipment(belgrad-1531), Equipment(belgrad-1532), ...]

>>> # ServiceStatus Sorgusu
>>> ServiceStatus.query.filter_by(
...     project_code='belgrad',
...     date='2026-02-20'
... ).all()
[ServiceStatus(belgrad-1531, "Servis"),
 ServiceStatus(belgrad-1532, "Servis Dışı"),
 ...]

>>> # Excel OKU
>>> import pandas as pd
>>> df = pd.read_excel('data/belgrad/Veriler.xlsx', sheet_name='Sayfa2')
>>> tram_ids = df['tram_id'].tolist()
>>> tram_ids
[1531, 1532, 1533, ...]
"""

print(reference)
