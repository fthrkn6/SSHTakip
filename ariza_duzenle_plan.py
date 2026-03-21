#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ARIZA DÜZENLEME VE FRACAS GÜNCELLEME ÖZELLİĞİ
Teknik Açıklama ve Uygulama Planı
"""

print("\n" + "="*280)
print("ARIZA DÜZENLEME + FRACAS OTOMATIK GÜNCELLEME ÖZELLİĞİ".center(280))
print("="*280 + "\n")

flow = """
CURRENT STATE (Mevcut Durum)
═══════════════════════════════════════════════════════════════════════════════════════════════════════

1. Dashboard → "Veriler" sekmesi → Arıza listesi tablosu
2. Tabloya tıklanıp detay sayfasına gidiliyor
3. Detay sayfasında arıza bilgileri gösteriliyor (READ-ONLY)
4. Düzenleme yok ❌

PLAN (Yeni Özellik)
═══════════════════════════════════════════════════════════════════════════════════════════════════════

1. Arıza Detay Sayfasına "Düzenle" Butonu Ekle
   ├─ Button: "📝 Düzenle" (mavi renkli)
   └─ Tıklayınca edit modal/form açılacak

2. Arıza Düzenleme Formu Oluştur
   ├─ Fields:
   │  ├─ Arıza Tarihi
   │  ├─ Arıza Tanımı
   │  ├─ Arıza Sınıfı (A/B/C)
   │  ├─ Arıza Tipi (Mekanik/Elektrik/etc)
   │  ├─ Araç
   │  ├─ Tamir Süresi (dakika)
   │  ├─ Tedarikçi
   │  └─ Çözüm/Notlar
   │
   └─ Save buttonu

3. Form Gönderilince Yapılacaklar:
   ├─ Veritabanı (Failure tablosu) güncelle
   ├─ FRACAS Excel dosyasını oku (logs/{project}/ariza_listesi/Fracas_*.xlsx)
   ├─ Arızanın satırını bul (FRACAS ID ile match)
   ├─ Sütunları güncelle:
   │  ├─ Arıza Tanımı sütunu
   │  ├─ Arıza Sınıfı sütunu
   │  ├─ Tamir Süresi sütunu (V/AB/AC sütunlarından birine)
   │  ├─ Tedarikçi sütunu
   │  └─ Düzenleme tarihi sütunu (yeni bir sütun ekle)
   │
   ├─ Excel dosyasını kaydet
   └─ Başarılı mesaj göster

HTTP FLOW
═══════════════════════════════════════════════════════════════════════════════════════════════════════

GET /arizalar/<ariza_id>
    ↓
    Template: failure/detail.html (CURRENT)
    - Arıza bilgileri görüntüleniyor
    - ŞİMDİ: "Düzenle" butonu ekle
    ↓
    [Kullanıcı "Düzenle" tıklıyor]
    ↓
POST /arizalar/<ariza_id>/duzenle (YENİ ROUTE)
    ↓
    Backend:
    ├─ Veritabanını güncelle (Failure tablosu)
    ├─ FRACAS Excel okun
    ├─ Satırı bul (FRACAS_ID match)
    ├─ Sütunları güncelle
    ├─ Excel kaydet
    └─ Success response döndür
    ↓
    Redirect: /arizalar/<ariza_id> (detail sayfasına geri dön)

DATABASE CHANGES
═══════════════════════════════════════════════════════════════════════════════════════════════════════

Failure tablosu (mevcut alanlar):
  - id (PK)
  - failure_code
  - equipment_id
  - failure_date
  - description
  - severity
  - failure_type
  - reported_by
  - resolved
  - ...

YENİ ALANLAR (opsiyonel):
  - fracas_id (Excel'deki "FRACAS ID" ile link)
  - last_updated_by (son kimin düzenlediceği)
  - last_updated_at (son düzenleme tarihi)

EXCEL SÜTUN MAPPING
═══════════════════════════════════════════════════════════════════════════════════════════════════════

FRACAS.xlsx (FRACAS sheet, header=4, yani satır 4):

Sütun İsimleri (Belgrad örneği):
  ├─ FRACAS ID (Unique ID - arızayı bulmak için kullan)
  ├─ Arıza Tanımı → Form: ariza_tanimi
  ├─ Arıza Sınıfı (A/B/C) → Form: ariza_sinifi
  ├─ İlgili Tedarikçi → Form: tedarikci
  ├─ Tamir Süresi (dakika) - V sütunu →Form: tamir_suresi
  ├─ Tamir/Değiştirme Başlama Tarihi
  ├─ Tamir/Değiştirme Bitiş Tarihi
  └─ ...

DOSYA DEĞIŞLIKLERI
═══════════════════════════════════════════════════════════════════════════════════════════════════════

1. templates/failure/detail.html (MEVCUT)
   ├─ "Düzenle" butonu ekle (mavi, modal/form aç)
   └─ Modal form ekle (HTML)

2. routes/failure.py (YENİ ROUTE)
   ├─ @bp.route('/<int:id>/duzenle', methods=['POST'])
   ├─ POST verilerini oku
   ├─ Failure tablosunu güncelle
   ├─ _update_fracas_file() fonksiyonu çağır
   └─ Başarı mesajı döndür

3. utils_fracas_updater.py (YENİ DOSYA)
   ├─ def update_fracas_file(project_name, fracas_id, updates)
   │  ├─ FRACAS dosyasını oku
   │  ├─ FRACAS ID ile satırı bul
   │  ├─ Sütunları güncelle
   │  ├─ Excel kaydet
   │  └─ Success/Error döndür
   └─ Hata yönetimi (logging)

ÖRNEK
═══════════════════════════════════════════════════════════════════════════════════════════════════════

Senaryö: Kocaeli'deki bir arızayı düzenliyoz

1. Dashboard → "Veriler" → Arıza listesi tablosu
   │
   ├─ FRACAS ID: 12345
   ├─ Araç: KOC-001
   ├─ Arıza Tanımı: "Motor kapağı açılmıyor"
   ├─ Arıza Sınıfı: "B"
   └─ Tamir Süresi: "240 dakika"

2. Detay sayfasına git (/arizalar/12345)

3. "Düzenle" butonu tıkla
   │
   └─ Modal açılır:
      ├─ Arıza Tanımı: "__________" (text area)
      ├─ Arıza Sınıfı: [Seçim: A/B/C]
      ├─ Tamir Süresi: "____" dakika (number)
      └─ "Kaydet" / "İptal" butonları

4. Bilgileri düzenle:
   ├─ Arıza Tanımı: "Motor kapağının açılış mekanizması tamir edildi"
   ├─ Arıza Sınıfı: "C" (B'den C'ye değiştir)
   └─ Tamir Süresi: "180" dakika (240'dan 180'e azalt)

5. "Kaydet" tıkla
   │
   ├─ POST /arizalar/12345/duzenle
   │  ├─ Failure.description = "Motor kapağının açılış mekanizması tamir edildi"
   │  ├─ Failure.severity = "C"
   │  ├─ Failure.tamir_suresi = 180
   │  └─ Failure.last_updated_at = NOW()
   │
   └─ _update_fracas_file('kocaeli', 'FRACAS-12345', {
        'ariza_tanimi': "Motor kapağının açılış...",
        'ariza_sinifi': "C",
        'tamir_suresi': 180
      })
           │
           ├─ logs/kocaeli/ariza_listesi/Fracas_KOCAELI.xlsx aç
           ├─ FRACAS sheet'ide FRACAS ID = 12345 olan satırı bul
           ├─ Sütunları güncelle:
           │  ├─ "Arıza Tanımı" sütunu → "Motor kapağının..."
           │  ├─ "Arıza Sınıfı" sütunu → "C"
           │  └─ "Tamir Süresi (dakika)" sütunu → 180
           │
           ├─ Excel kaydet
           └─ SUCCESS

6. Başarı mesajı: "✓ Arıza başarıyla güncelleştirildi"

7. Detay sayfasına geri dön (/arizalar/12345)
   └─ Güncellenmiş bilgiler gösteriliyor


AVANTAJLAR
═══════════════════════════════════════════════════════════════════════════════════════════════════════

✓ Dashboard'dan doğrudan Excel'i güncelleyebilir
✓ FRACAS dosyası otomatik güncellenir
✓ KPI'lar (MTTR, arıza sınıfı) otomatik yeniden hesaplanır
✓ Audit trail: last_updated_at ve last_updated_by kaydedilir
✓ Real-time senkronizasyon


TEKNIK KONSERNLER
═══════════════════════════════════════════════════════════════════════════════════════════════════════

1. Excel Sütun Mapping
   ✓ Her proje için farklı sütun indexi olabilir (header satırı farklı)
   → Solution: ProjectManager'dan sütun mapping'ini otomatik oku

2. FRACAS ID Bulma
   ✓ FRACAS sheet'inde unique ID sütunu olmalı
   → Kullan: 'FRACAS ID' sütunu

3. Dosya Kilitleme (Lock)
   ✓ Excel dosyası açıkken edit edilebilir mi?
   → Solution: openpyxl load_workbook() → save() (test etmek gerekebilir)

4. Hata Yönetimi
   ✓ Ne olur dosya kritik değiştirilirse?
   → Solution: Try-except, logging, user feedback

5. Permission (İzin Kontrol)
   ✓ Kim düzenleyebilir?
   → Solution: Tüm kullanıcılar (şimdilik), sonra role-based ekle


YAPILACAKLAR ÖZET
═══════════════════════════════════════════════════════════════════════════════════════════════════════

[ ] 1. Failure modeline yeni alanlar ekle (fracas_id, last_updated_by, last_updated_at)
[ ] 2. failure/detail.html'ye "Düzenle" butonu ekle + modal form yapısı
[ ] 3. routes/failure.py'ye new route ekle: /<int:id>/duzenle
[ ] 4. utils_fracas_updater.py oluştur (Excel güncelleme logic'i)
[ ] 5. TestEDIT fonksiyonlarını test et
[ ] 6. Tüm 8 projekte test et
"""

print(flow)
print("\n" + "="*280 + "\n")
