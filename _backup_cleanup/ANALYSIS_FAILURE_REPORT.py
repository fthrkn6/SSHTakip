"""
ARIZA BİLDİRME - ANALİZ VE ÖNERİLER

MEVCUT DURUM:
============
1. Arıza Bildirme Route: /yeni-ariza-bildir (app.py line 281)
   - Form'dan veri alıyor ✓
   - FRACAS Excel dosyasını bulmaya çalışıyor ✓
   - Excel'e yazıyor (wb.save) ✓

2. Problem Noktaları:
   - Header satırı 4. satırda bekleniyor (line 520)
   - Veriler.xlsx ve FRACAS dosyasının format uyuşmazlığı olabilir
   - Excel'e yazırken sütun eşleştirmesi başarısız olabilir

3. Mevcut Excel Yapısı:
   - /data/belgrad/Veriler.xlsx (Sayfa1, Sayfa2)
   - /data/belgrad/ içinde FRACAS dosyası (tam adı bilinmiyor)


SEÇENEKLERİ DEĞERLENDİRME:
==========================

SEÇENEK 1: Eski FRACAS Excel'ine Yazıyı Düzelt
─────────────────────────────────────────────
✓ AVANTAJLARI:
  - Mevcut Excel yapısı korunur
  - Tek bir merkezi dosya
  - Minimum kod değişikliği

✗ DEZAVANTAJLARI:
  - Header satırı pozisyonunu doğru belirleme gerekli
  - Sütun eşleştirmesi yeniden yapılmalı
  - Excel formatı standardize edilmeli

ÖNERİLEN ÇALIŞMA:
  1. FRACAS Excel dosyasını İncele (header satırı, sütun adları)
  2. app.py line 520'deki header tanımını düzelt
  3. Sütun eşleştirmesini kontrol et
  4. Test et


SEÇENEK 2: Yeni Arıza Listesi Oluştur (Tavsiye Edilen)
──────────────────────────────────────────────────────
✓ AVANTAJLARI:
  - Temiz ve standardize yapı
  - Arıza ve FRACAS ayrı tutulur
  - Gelişmeye uygun
  - /logs/ariza_listesi/ klasöründe saklanır

✗ DEZAVANTAJLARI:
  - İki dosya yönetimi
  - Biraz daha kod gerekli

OLUŞTURULACAK YAPISI:
  Folder: /logs/ariza_listesi/
  Files:
    - Ariza_Listesi_{PROJE}_{TARIH}.xlsx
    - Schema: FRACAS ID | Araç No | Sistem | Alt Sistem | Tarih | Durum | ...
    - Otomatik olarak tarihe göre yedek tutulur


TAVSIYE:
=========
→ SEÇENEK 2'yi uygula çünkü:
  1. FRACAS Excel'in sorunu ne olduğunu bilmiyoruz
  2. Arıza Listesi ile FRACAS'ı ayrı tutmak daha mantıklı
  3. Arıza bildirme form'u doğru çalışacak
  4. Her gün yeni dosya = otomatik yedekleme

Hangi seçeneği istiyorsun?
"""
print(__doc__)
