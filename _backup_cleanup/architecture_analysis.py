#!/usr/bin/env python3
"""MIMARI ANALIZ - Tek Kaynaktan (Excel) vs 2 Tablo Sistemi"""
import sys
sys.path.insert(0, '.')

from datetime import date

print("\n" + "="*120)
print("🏛️  MIMARI ANALIZ - İKİ SEÇENEK")
print("="*120 + "\n")

print("""
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ SEÇENEK 1: TEK KAYNAKTAN (EXCEL)                                                                    │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤

Veri Yapısı:
  Excel (Veriler.xlsx) - Sayfa2:
  ┌─────────────────────────────────────────────────────────┐
  │ equipment_code │ name │ status │ sistem │ alt_sistem   │
  ├─────────────────────────────────────────────────────────┤
  │ 1531           │ ...  │ Servis │ Motor  │ Elektrik     │
  │ 1532           │ ...  │ Aktif  │        │              │
  │ 1556           │ (YENİ) NEW  │        │              │
  └─────────────────────────────────────────────────────────┘

Avantajları:
  ✅ Tek veri kaynağı = basit, merkezi
  ✅ Excel'de her değişiklik = anında tüm sayfalar güncellenir
  ✅ Veritabanı'ya bağımlı değil
  ✅ Yedekleme kolay (Excel dosyası)
  ✅ User-friendly (Excel açıp drag-drop)

Dezavantajları:
  ❌ Her araç için her gün status Excel'de tutulmalı
  ❌ Tarihsel veri (geçmiş günler) Excel'de çok satır = büyük dosya
  ❌ MTBF, MTTR, availability hesapları için tarihsel veri gerekli
  ❌ Raporlama (2 ay önceki veri?) Excel'de yapılmaz
  ❌ Real-time queries yavaş
  ❌ Para & malzemenin saati, bakım maliyeti izleme zor
  
Örnek:
  2026-02-20: 1531=Servis, 1532=Aktif, 1533=Arızalı
  2026-02-21: 1531=Aktif, 1532=Servis, 1533=Aktif
  2026-02-22: ...
  
  26 araç × 365 gün = 9490 satır/yıl
  Çok sayfalı Excel → Yavaş ve karmaşık

└─────────────────────────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ SEÇENEK 2: İKİ TABLO SİSTEMİ (CURRENT - ÖNERILEN)                                                   │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤

Veri Yapısı:
  Excel (Veriler.xlsx) - Sayfa2:               Database (PostgreSQL/SQLite):
  ┌──────────────────────────────┐             ┌─────────────────────────┐
  │ equipment_code │ name │ ...  │────┐        │ Equipment Table         │
  │ 1531           │ ...  │      │    └───────→├─────────────────────────┤
  │ 1556           │ (YENİ)       │            │ id   equipment_code mtbf│
  └──────────────────────────────┘            │ 1    1531           600 │
                                               │ 26   1556           600 │
                                               └─────────────────────────┘
                                               
  Dinamik Veriler:
  ┌──────────────────────────────────────────┐
  │ ServiceStatus Table                       │
  ├──────────────────────────────────────────┤
  │ tram_id │ date       │ status │ ...      │
  │ 1531    │ 2026-02-20 │ Servis │          │
  │ 1532    │ 2026-02-20 │ Aktif  │          │
  │ 1556    │ 2026-02-20 │ Aktif  │ (YENİ)   │
  │ 1531    │ 2026-02-19 │ Aktif  │ (GEÇMİŞ) │
  └──────────────────────────────────────────┘

Avantajları:
  ✅ Equipment = Static araç bilgileri (teknik spec, MTBF, kritikallik)
  ✅ ServiceStatus = Dynamic günlük durumu (tarihsel)
  ✅ Tarihsel veriler kolayca saklanır ve sorgulanır
  ✅ MTBF, MTTR, Availability gibi metrikler hesaplanır
  ✅ Dashboard (26 araç) çabuk yüklenebilir (Equipment'ten çek)
  ✅ Service Status tablosu her araç × her gün için kayıt tutar
  ✅ Excel'i referans olarak kullanırız (senkronizasyon için)
  ✅ Raporlar dinamik oluşturulur (tarihe göre filter)
  ✅ Maintenance scheduling, FRACAS, RCA gibi kompleks iş akışları destekler

Dezavantajları:
  ❌ 2 veri kaynağını senkronize tutmalısınız
  ❌ Biraz daha karmaşık mimari
  
Tarihsel Veri Örneği (26 araç × 90 gün = 2340 satır):
  2026-02-20: [1531:Servis, 1532:Aktif, ... 1556:Aktif]
  2026-02-19: [1531:Aktif, 1532:Servis, ... 1556:Servis]
  ...
  2025-11-20: [eski veriler]
  
  → MTBF hesabı: Arız başlangıç → Arız sonu = süre
  → Availability: (Çalışma Saati) / (Toplam Saat)
  → Trend: "Eylül'de kaç kez arızalandı"

└─────────────────────────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ SONUÇ: HANGI BİRİ SEÇMELIYIM?                                                                       │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤

🎯 ÖNERILEN: SEÇENEK 2 (İKİ TABLO)

Neden?
  1. Equipment = referans veri (SİZİN KONTROL ETTİĞİNİZ Excel dosyası)
  2. ServiceStatus = operasyonel veri (sistem tarafından kaydediliyor)
  3. Excel'i "malzeme listesi" gibi tutabilirsiniz
  4. Ama GERÇEK veriler veritabanında (güvenilir, sorgulanabilir)

Mevcut Durum:
  ✅ Excel: 26 araç (equipment kaynak)
  ✅ Equipment Table: 26 araç (Excel'le senkronize)
  ✅ ServiceStatus: 26 araç, bugün (günlük durum)

YANANI ÇÖZMEK:
  Excel'de update → Equipment table güncelle
  ServiceStatus → Sistem otomatik kaydediyor

┌────────────────────────────────────────────┐
│ Aktarma Flow                               │
├────────────────────────────────────────────┤
│ Excel (Referans) ─────┐                    │
│   ↓                    ↓                   │
│ Equipment Table   ServiceStatus Table      │
│   ↓                    ↑                   │
│ [Her gün GET]    [Her gün INSERT]         │
│   ↓                    ↑                   │
│ Dashboard        Dashboard + Status Sayfası│
└────────────────────────────────────────────┘

""")

print("="*120)
print("📌 KARARıNız: İKİ TABLO Mı TUTMAYA DEVAM EFELIM? YOKSA TEK EXCEL'E GEÇELİM?")
print("="*120 + "\n")
