# Bozankaya CMMS - Tüm Proje Senaryoları ve Gereksinimler

**Tarih**: 2024  
**Sistem**: Computerized Maintenance Management System (CMMS)  
**Domain**: Tramvay Bakım Yönetimi  
**Standartlar**: ISO 55000, EN 15341, EN 13306, ISO 27001

---

## İÇİNDEKİLER

1. [Kullanıcı Rolleri ve Izinleri](#1-kullanıcı-rolleri-ve-izinleri)
2. [Veri Modelleri ve İlişkileri](#2-veri-modelleri-ve-ilişkileri)
3. [Temel İş Akışları (Use Cases)](#3-temel-iş-akışları-use-cases)
4. [Özellikler ve Fonksiyonlar](#4-özellikler-ve-fonksiyonlar)
5. [Validasyon Kuralları](#5-validasyon-kuralları)
6. [Entegrasyon Noktaları](#6-entegrasyon-noktaları)
7. [Raporlama ve Analytics](#7-raporlama-ve-analytics)
8. [Güvenlik Gereksinimleri](#8-güvenlik-gereksinimleri)

---

## 1. KULLANICI ROLLERI VE İZİNLERİ

### 1.1 Rol Tanımları

#### ADMIN (Sistem Yöneticisi)
- **Izinler**: Tüm işlemlere tam erişim
- **Sorumluluklar**:
  - Kullanıcı yönetimi (oluştur, sil, izin değiştir)
  - Sistem konfigürasyonu
  - Yedek parça ve ekipman katalogu yönetimi
  - Raporlar ve dışa aktarma
  - Denetim günlüğü (Audit Log) inceleme
- **Erişim**: Tüm menüler ve fonksiyonlar

#### MUHENDIS (Mühendis)
- **Izinler**: Planlama ve analiz
- **Sorumluluklar**:
  - Bakım planları oluşturma ve güncelleme
  - Öngörücü bakım analizi
  - KPI raporları oluşturma
  - Teknik dokümantasyon yönetimi
  - Ekipman sınıflandırması ve hiyerarşisi
- **Erişim**: Ekipman, Bakım Planları, KPI Dashboard, Raporlar

#### TEKNİSYEN (Teknik Personel)
- **Izinler**: İş emrini gerçekleştirme
- **Sorumluluklar**:
  - Kendilerine atanan iş emirlerini tamamlama
  - Arıza raporları güncelleme
  - İş tamamlama notları yazma
  - Malzeme kullanım kaydı yapma
- **Erişim**: Kendi iş emirleri, Ekipman detayları (oku), Arıza raporları (oku/güncelle)

#### OPERATÖR (İşletme Sorumlusu)
- **Izinler**: Arıza bildirme ve izleme
- **Sorumluluklar**:
  - Arıza bildirme
  - İş emri durumunu izleme
  - Sistem performansı raporları görüntüleme
- **Erişim**: Arıza bildirimi (yeni), KPI Dashboard (oku-sadece)

---

## 2. VERI MODELLERI VE İLİŞKİLERİ

### 2.1 Temel Modeller

#### USER (Kullanıcı)
```
Alanlar:
- id (PK)
- username (unique, required)
- email (unique, required)
- password_hash
- full_name
- role (admin, muhendis, teknisyen, operatör)
- department (İnsan Kaynakları, Teknik Bakım, Operasyon)
- phone, employee_id
- hourly_rate (€/saat)
- is_active (boolean)
- last_login (datetime)
- created_at, updated_at

İleri Özellikler:
- skills (JSON): Teknik beceriler listesi ["elektrik", "mekanik", "hidrolik"]
- certifications (JSON): Sertifika bilgileri
- skill_level (junior, mid, senior, expert)
- work_location: Çalışma yeri
- shift_pattern: Vardiya düzeni
- max_weekly_hours, current_weekly_hours: Saat takibi
- is_available: Müsaitlik durumu
- availability_notes: Müsaitlik açıklaması

İlişkiler:
- created_work_orders (1:N)
- assigned_work_orders (1:N)
- reported_failures (1:N)
- assigned_failures (1:N)
- audit_logs (1:N)
```

#### EQUIPMENT (Ekipman)
```
Alanlar:
- id (PK)
- equipment_code (unique, required): "TRN-001", "VAG-001-FREIN"
- name, equipment_type (tren, vagon, motor, fren, kapı, ac, elektrik)
- manufacturer, model, serial_number
- location
- status (aktif, bakımda, arızalı, depo)
- criticality (low, medium, high, critical)
- installation_date, warranty_end_date, last_maintenance_date
- total_km, total_hours, cycle_count
- acquisition_cost, total_maintenance_cost
- mtbf_hours, mttr_hours
- availability_rate (%), reliability_rate (%)
- total_downtime_planned, total_downtime_unplanned (dakika)

Aşınma ve Tetikleme:
- km_threshold, hours_threshold, cycle_threshold: Bakım tetikleme değerleri
- wear_level (%): Mevcut aşınma seviyesi
- wear_threshold (%): Uyarı eşiği (default 80%)
- last_km_at_maintenance, last_hours_at_maintenance

Hiyerarşi:
- hierarchy_level (1:Tren, 2:Alt Sistem, 3:Parça)
- hierarchy_path: "TRN-001/SYS-FREN/PRT-DISK"
- parent_id (FK): Üst ekipman

Gereksinimler:
- required_skills (JSON): ["mekanik_ileri", "elektrik"]
- technical_specs (Text)
- notes

İlişkiler:
- parent_equipment (N:1)
- children_equipment (1:N)
- failures (1:N)
- work_orders (1:N)
- maintenance_plans (1:N)
- downtimes (1:N)
- meter_readings (1:N)
- documents (1:N)
```

#### FAILURE (Arıza Kaydı)
```
Alanlar:
- id (PK)
- failure_code (unique, required): "ARZ-2024-001"
- equipment_id (FK, required)
- title, description
- severity (kritik, yüksek, orta, düşük)
- failure_type: Arıza türü
- failure_mode: Arıza modu
- root_cause: Kök neden
- status (açık, devam_ediyor, çözüldü)
- reported_by (FK), assigned_to (FK), resolved_by (FK)
- failure_date, detected_date, resolved_date
- downtime_minutes: Kaç dakika inoperatif oldu
- repair_cost (€)
- impact_description: Etki açıklaması
- resolution_notes, corrective_action, preventive_action
- created_at, updated_at

İlişkiler:
- equipment (N:1)
- reporter (N:1 User)
- assignee (N:1 User)
- resolver (N:1 User)
- work_orders (1:N)
- root_cause_analysis (1:1)
```

#### WORK_ORDER (İş Emri)
```
Alanlar:
- id (PK)
- order_code (unique): "IS-2024-001"
- equipment_id (FK, required)
- failure_id (FK, nullable): Arızadan bağlantı
- maintenance_plan_id (FK, nullable): Plan dari bağlantı
- title, description
- work_type (ariza_onarim, periyodik_bakim, koruyucu_bakim, revizyon, muayene)
- priority (acil, yuksek, normal, dusuk)
- status (beklemede, onay_bekliyor, devam_ediyor, tamamlandi, iptal)
- created_by (FK), assigned_to (FK), approved_by (FK)
- planned_start, planned_end
- actual_start, actual_end, completed_date
- work_instructions (Text)
- safety_notes (Text)
- completion_notes (Text)
- labor_hours, labor_cost (€)
- material_cost (€)
- external_cost (€) [Yüklenici maliyeti]
- total_cost (€)
- downtime_minutes
- checklist (JSON): Yapılması gereken kontroller
- checklist_completed (boolean)
- created_at, updated_at

İlişkiler:
- equipment (N:1)
- failure (N:1, nullable)
- creator (N:1 User)
- assignee (N:1 User)
- approver (N:1 User)
- parts_used (1:N WorkOrderPart)
- time_logs (1:N)
```

#### MAINTENANCE_PLAN (Bakım Planı)
```
Alanlar:
- id (PK)
- plan_code (unique): "BAK-2024-001"
- equipment_id (FK, required)
- title, description
- plan_type (periyodik, koşulu, duruş)
- maintenance_type (koruyucu, imaale, revizyon, muayene)
- frequency_value (int): Sıklık değeri
- frequency_unit (gün, saat, km, döngü): Sıklık birimi
- next_due_date (datetime)
- last_executed_date (datetime)
- estimated_duration_hours
- estimated_cost (€)
- created_by (FK)
- is_active (boolean)
- created_at, updated_at

Tetikleme:
- km_threshold, hours_threshold: Aşınma eşikleri
- cycle_threshold: Döngü eşiği
- wear_level_threshold: Aşınma seviyesi

İlişkiler:
- equipment (N:1)
- creator (N:1 User)
- work_orders (1:N)
```

#### SPARE_PART_INVENTORY (Yedek Parça Envanteri)
```
Alanlar:
- id (PK)
- part_code (unique): "YED-FREIN-001"
- part_name, description
- manufacturer, part_number
- unit_price (€)
- quantity_in_stock (int)
- reorder_level (int): Min stok seviyesi
- reorder_quantity (int): Sipariş miktarı
- location: Depo konumu
- lead_time_days: Tedarik süresi
- compatible_equipment_ids (JSON): ["EQ1", "EQ2"]
- supplier_id (FK)
- last_received_date
- last_used_date
- expiry_date (nullable): Parçanın ömrü
- is_active (boolean)
- created_at, updated_at

İlişkiler:
- usage_records (1:N WorkOrderPart)
- supplier (N:1)
```

#### DOWNTIME_RECORD (Duruş Kaydı)
```
Alanlar:
- id (PK)
- equipment_id (FK, required)
- failure_id (FK, nullable)
- start_time (datetime, required)
- end_time (datetime)
- duration_minutes (int)
- downtime_type (planlı, planlamayan)
- reason (arıza, bakım, revizyon, muayene, kontrol)
- notes (Text)
- created_at

İlişkiler:
- equipment (N:1)
- failure (N:1, nullable)
```

### 2.2 KPI ve Analiz Modelleri

#### KPI_SNAPSHOT (KPI Anlık Görüntüsü)
```
Alanlar:
- id (PK)
- equipment_id (FK)
- measurement_date (datetime)
- mtbf_hours: Mean Time Between Failures
- mttr_hours: Mean Time To Repair
- availability_percentage: Kullanılabilirlik (%)
- reliability_rate: Güvenilirlik (%)
- oee: Overall Equipment Effectiveness (%)
- maintenance_cost_ratio: Bakım maliyeti/Satın alma maliyeti (%)
- mean_downtime: Ortalama duruş süresi (dakika)
- created_at
```

#### EN15341_KPI (EN 15341 Standardı KPI)
```
Alanlar:
- id (PK)
- equipment_id (FK)
- period_start, period_end (tarih)
- po_mtbf: Technical - MTBF (saat)
- po_mttr: Technical - MTTR (saat)
- po_availability: Technical - Availability (%)
- po_performance: Technical - Performance (%)
- po_quality: Technical - Quality (%)
- cost_preventive_maintenance: Maliyet - Preventif (€)
- cost_corrective_maintenance: Maliyet - Korektif (€)
- cost_total_maintenance: Maliyet - Toplam (€)
- po_cost_ratio: Maliyet - Oran (%)
- created_at
```

#### METER_READING (Ölçüm Okuma)
```
Alanlar:
- id (PK)
- equipment_id (FK)
- reading_type (km, saat, döngü, sıcaklık)
- reading_value (float)
- reading_date (datetime)
- notes
- recorded_by (FK User)
```

#### SENSOR_DATA (Sensör Verisi) [IoT Entegrasyonu]
```
Alanlar:
- id (PK)
- equipment_id (FK)
- sensor_type (sıcaklık, titreşim, basınç, akım)
- sensor_id (string): Fiziksel sensör ID
- value (float): Okuma değeri
- unit (°C, mm/s, bar, A)
- is_anomaly (boolean): Anomali belirlendi mi
- anomaly_score (float): 0-1 anomali skoru
- reading_timestamp (datetime)
- received_at (datetime)
- raw_data (JSON): Ham sensör verisi
```

---

## 3. TEMEL İŞ AKIŞLARI (USE CASES)

### 3.1 ARIZA RAPORLAMA VE YÖNETİMİ

#### Senaryo UC-1: Arıza Bildirimi
**Aktör**: Operatör  
**Ön Koşul**: Sistem çalışıyor, operatör giriş yaptı

**Adımlar**:
1. "Arıza Bildir" butonuna tıkla
2. Ekipman seç (dropdown)
3. Arıza başlığı ve açıklaması gir
4. Önem seviyesi seç (kritik/yüksek/orta/düşük)
5. "Gönder" butonuna tıkla
6. Sistem otomatik olarak:
   - failure_code oluşturur ("ARZ-2024-001")
   - Ekipman durumunu "arızalı" olarak işaretler
   - Admin ve sorumlu mühendise bildirim gönderir
   - Duruş kaydı başlatır

**Çıktı**: Arıza kaydı oluşturulur, iş emri oluşturma akışı başlar

#### Senaryo UC-2: Arıza Analiz ve Atama
**Aktör**: Mühendis  
**Ön Koşul**: Arıza raporlanmış

**Adımlar**:
1. "Açık Arızalar" listesini görüntüle
2. Arızayı seç
3. Ayrıntıları incele:
   - Ekipman geçmişi ve arıza sayısı
   - Benzer arızalar (AI önerisi)
   - KPI etkisi
4. Arıza türü seç (mekanik/elektrik/hidrolik/diğer)
5. Kök neden analizi yap (dropdown menüler)
6. Uygun teknisyeni seç (beceri ve müsaitlik bazlı)
7. İş emri oluştur veya mevcut plana ekle
8. "Ata ve Kaydet" butonuna tıkla

**Çıktı**: WorkOrder oluşturulur, teknisyene bildirim gönderilir

#### Senaryo UC-3: Arıza Çözümü ve Kapatma
**Aktör**: Teknisyen  
**Ön Koşul**: İş emri atanmış, uygulanmış

**Adımlar**:
1. Kendi iş emirlerini görüntüle
2. Tamamlanan işi seç
3. "Tamamlama Formu"nu doldur:
   - Yapılan işlem açıklaması
   - Kullanılan malzeme ve parçalar
   - Gerçek çalışma saati
   - Maaliyet doğrulaması
4. Resimler/video ekle (opsiyonel)
5. "Tamamla" butonuna tıkla
6. Sistem:
   - Arıza durumunu "çözüldü" olarak işaretler
   - Duruş süresini hesaplar
   - Maliyeti kaydeder
   - MTTR güncellemeleri yap
   - Mühendise onay isteği gönder

**Çıktı**: Arıza kapatılır, veriler KPI hesaplamalarına girer

---

### 3.2 BAKIM PLANI VE PLANLAMA

#### Senaryo UC-4: Bakım Planı Oluşturma
**Aktör**: Mühendis  
**Ön Koşul**: Ekipman kayıtlı

**Adımlar**:
1. Ekipman seç
2. "Bakım Planları" sekmesi aç
3. Yeni plan oluştur:
   - Plan adı: "Motor Periyodik Bakım"
   - Plan tipi: Periyodik / Koşul
   - Bakım tipi: Koruyucu / İmaale / Revizyon
   - Sıklık: "Her 500 km" veya "Ayda bir"
4. Tetikleme eşikleri ayarla:
   - km_threshold: 500
   - hours_threshold: 100
   - wear_threshold: 75%
5. Tahmini maliyet ve süre gir
6. Ek notlar ve talimatlar ekle
7. "Kaydet" butonuna tıkla
8. Sistem:
   - İlk next_due_date hesaplar
   - Uyarı ayarlar
   - İş emri şablonu oluşturur

**Çıktı**: Bakım planı aktivate edilir, otomat iş emri yaratma tetiklenir

#### Senaryo UC-5: Otomatik İş Emri Oluşturma
**Sistem Tetiklemesi**: Zamanlayıcı (her gün çalışır)

**Adımlar**:
1. Tüm aktif bakım planlarını kontrol et
2. Her plan için:
   - Ekipman ölçümlerini kontrol et (km, saat, döngü)
   - Aşınma seviyesini hesapla
   - next_due_date ile bugün karşılaştır
3. Tetikleme şartı karşılanmışsa:
   - WorkOrder otomatik oluştur
   - order_code oluştur
   - Uygun teknisyenleri seç (beceri + müsaitlik)
   - Bildirim gönder
   - Status "beklemede" olarak ayarla
4. Sistem log kaydı yap

**Çıktı**: Bakım iş emirleri otomatik planlanır

---

### 3.3 KAYNAK YÖNETİMİ

#### Senaryo UC-6: İş Emrine Kaynak Atama
**Aktör**: Mühendis  
**Ön Koşul**: WorkOrder oluşturulmuş

**Adımlar**:
1. Açık iş emirlerini listele
2. İş emrini seç
3. "Kaynak Atama" bölümü aç
4. Teknisyen seçim:
   - Gerekli beceriler: "elektrik_orta", "mekanik"
   - Müsaitlik durumu kontrol et
   - Vardiya düzeni kontrol et
   - Haftalık saat yükü kontrol et
5. İlgili teknisyenleri listele (uygunluk puanı ile)
6. Teknisyeni seç
7. Planlanan başlangıç/bitiş tarihi ayarla
8. Yedek parçalar seç:
   - Part kodu gir veya listeden seç
   - Miktar gir
   - Stok kontrol otomatik
   - Eksikse, reorder bildirim gönder
9. "Ata ve Onayla" butonuna tıkla

**Çıktı**: Kaynak atanır, maliyet tahmini yapılır, teknisyene bildirim gönderilir

#### Senaryo UC-7: Yedek Parça Yönetimi
**Aktör**: Admin  
**Ön Koşul**: Parça envanteri oluşturulmuş

**Adımlar**:
1. "Yedek Parçalar" menüsü aç
2. "Stok Durumu" raporunu gör
3. Düşük stoklu parçaları tanımla (quantity_in_stock < reorder_level)
4. Eksik parçalar için otomatik:
   - Satıcıya sipariş oluştur
   - Bekleme listesi güncelle
5. Yeni parça geliş kaydı:
   - Part kod tarayıcıyla oku
   - Miktar doğrula
   - Giriş tarihi kaydet
   - Stok güncelle
6. Parça kullanım raporunu gör (iş emirlerine göre)

**Çıktı**: Parça envanteri yönetilir, eksikleri önlenir

---

### 3.4 KPI VE RAPORLAMA

#### Senaryo UC-8: Dashboard İzleme
**Aktör**: Yönetim  
**Ön Koşul**: Sistem en az 30 gün veri toplamış

**Adımlar**:
1. Dashboard sayfasını aç
2. Temel KPI'lar görüntüle:
   - Ortalama Kullanılabilirlik (%)
   - MTBF (saat)
   - MTTR (saat)
   - OEE (Overall Equipment Effectiveness)
   - Tahmini Aylık Bakım Maliyeti
3. Grafikler incele:
   - Arıza trendleri (zaman serisi)
   - Ekipman sağlığı (ısı haritası)
   - Bakım maliyeti dağılımı (pasta grafik)
4. Uyarıları kontrol et:
   - Kritik ekipmanlar
   - Gecikmiş bakım planları
   - Anomali algılamalar
5. Dönem filtresi uygula (bugün/hafta/ay/yıl/özel)
6. "PDF/Excel Dışa Aktar" butonuna tıkla

**Çıktı**: Yönetim bilgisi sağlanır, karar alma desteklenir

#### Senaryo UC-9: Detaylı Ekipman Raporu
**Aktör**: Mühendis  
**Ön Koşul**: Ekipman seçilmiş

**Adımlar**:
1. Ekipman seç
2. "Performans Raporu" oluştur:
   - Tarih aralığı seç
   - KPI'ları görüntüle (MTBF, MTTR, Availability)
   - Arıza geçmişi listele
   - Bakım işlemleri listele
   - Maliyetler özetle
   - Anomali trendleri göster
3. "EN 15341 Uyum Raporu" oluştur:
   - Teknik göstergeleri (PO-MTBF, PO-MTTR, vb.)
   - Maliyet göstergelerini göster
   - Uyum durumunu belirle
4. Önerileri görüntüle (AI-generated):
   - "Motor değişim önerilir (30 aya)"
   - "Bakım sıklığı artırılmalı"
5. Raporu PDF olarak karşıdan al

**Çıktı**: Detaylı analiz raporu sağlanır

---

### 3.5 GEÇMİŞ VERİSİ İDARESİ

#### Senaryo UC-10: Ölçüm Kaydı (Meter Reading)
**Aktör**: Operatör / Teknisyen  
**Ön Koşul**: Ekipman tanımlı

**Adımlar**:
1. Günlük turda: "Ölçüm Gir" butonuna tıkla
2. Ekipman seç
3. Ölçüm türü seç (km, saat, döngü)
4. Değer gir (örn: 15250 km)
5. Tarih/saati onayla (oto dolduruluş)
6. Not ekle (opsiyonel)
7. "Kaydet" butonuna tıkla
8. Sistem:
   - Aşınma seviyesini hesapla
   - Bakım tetikleme şartlarını kontrol et
   - Anomali yoksa tamamla
   - Anomali varsa uyar

**Çıktı**: Ekipman ölçümleri güncellenir, tetikleme kontrol edilir

---

## 4. ÖZELLİKLER VE FONKSIYONLAR

### 4.1 EKRAN / SAYFA LİSTESİ

| Sayfa | URL | Rol | Açıklama |
|-------|-----|-----|----------|
| Dashboard | `/dashboard` | Tüm | Ana izleme ve KPI gösterimi |
| Arızalar | `/arizalar` | Tüm | Arıza listesi ve yönetimi |
| Arıza Detay | `/ariza/<id>` | Tüm | Arıza detayları ve çözüm süreci |
| Arıza Bildirimi | `/ariza/new` | Operatör+ | Yeni arıza formu |
| Ekipmanlar | `/ekipmanlar` | Tüm | Ekipman listesi |
| Ekipman Detay | `/ekipman/<id>` | Tüm | Ekipman bilgileri, geçmiş, KPI |
| İş Emirleri | `/is-emirleri` | Tüm | İş emri listesi |
| İş Emri Detay | `/is-emri/<id>` | Tüm | İş emri detayları |
| İş Emri Oluştur | `/is-emri/new` | Mühendis+ | Yeni iş emri formu |
| Bakım Planları | `/bakim-planlari` | Mühendis+ | Bakım planları yönetimi |
| Plan Oluştur | `/bakim-plani/new` | Mühendis | Yeni plan formu |
| Yedek Parçalar | `/yedek-parcalar` | Admin+ | Stok yönetimi |
| Parça Ekleme | `/yedek-parca/new` | Admin | Yeni parça formu |
| Raporlar | `/raporlar` | Mühendis+ | Rapor seçimi ve üretimi |
| Kullanıcılar | `/kullanicilar` | Admin | Kullanıcı yönetimi |
| Profil | `/profil` | Tüm | Kişisel bilgileri düzenleme |
| Audit Log | `/audit-log` | Admin | Sistem etkinlikleri |

### 4.2 İŞLETİM ÖZELLİKLERİ

#### Aşınma Takibi
- Ekipman için 3 farklı metrik takibi: km, saat, döngü
- Aşınma seviyesi otomatik hesaplama
- Eşik değerlerine göre uyarı tetikleme
- Bakım sonrası meter sıfırla

#### Anomali Tespiti (AI)
- Sensör verilerinin real-time analizi
- Z-score ve Isolation Forest algoritmaları
- Anomali skoru (0-1) hesaplama
- Otomatik bildirim eşiği > 0.8
- Başarılı durumlar liste

#### Bildirim Sistemi
- Email bildirim (Flask-Mail)
- In-app notifications
- SMS (opsiyonel - Twilio)
- Bildirim tercihleri kullanıcı tarafından yönetilir

#### Raporlama
- PDF dışa aktar (ReportLab / WeasyPrint)
- Excel dışa aktar (openpyxl)
- Özelleştirilebilir şablonlar
- Otomatik zamanlı raporlar
- Email ile gönderme

---

## 5. VALIDASYON KURALLARI

### 5.1 Veri Validasyonları

#### User Modeli
- `username`: 3-50 karakter, alfanumerik + "_-"
- `email`: Geçerli email formatı
- `password`: Min 8 karakter, en az 1 büyük, 1 küçük, 1 sayı
- `hourly_rate`: >= 0, 2 decimal
- `max_weekly_hours`: 1-168

#### Equipment Modeli
- `equipment_code`: Unique, format "TYPE-XXX"
- `name`: 1-100 karakter
- `total_km`: >= 0
- `wear_level`: 0-100
- `maintenance_cost` <= `acquisition_cost * 3` (uyarı)

#### Failure Modeli
- `failure_code`: Auto-generate, unique
- `title`: 5-200 karakter
- `severity`: Enum (kritik, yüksek, orta, düşük)
- `downtime_minutes`: >= 0
- `repair_cost`: >= 0
- `failure_date` <= `resolved_date`

#### WorkOrder Modeli
- `order_code`: Auto-generate, unique
- `labor_hours`: >= 0
- `labor_cost`: >= 0
- `planned_start` <= `planned_end`
- `actual_start` <= `actual_end`
- Çalışma süresi planı (planned) < 12 saat uyarı ver

#### MaintenancePlan Modeli
- `frequency_value`: >= 1
- `frequency_unit`: Enum (gün, saat, km, döngü)
- `estimated_duration_hours`: >= 0.25
- `estimated_cost`: >= 0

### 5.2 İş Kuralları

#### Arıza Yönetimi
- Kritik arıza bildirimi alındığında, admin ve sorumlu mühendise saat başı bildirim gönder
- Açık arıza sayısı > 10 ise, yönetim uyarısı
- Aynı ekipman için 5 gün içinde 3. arıza: otomatik "ciddi problem" işareti

#### İş Emri Yönetimi
- İş emri 7 gün gecikirse, sorumlu müdüre bildirim
- İş emri atanırken, teknisyenin haftalık saat yükü kontrol edilir
- Tahmini maliyeti "Onay Limiti" aşarsa, mühendis onayı gerekir

#### Bakım Planlama
- Yeni plan oluşturulurken ilk next_due_date = today() + frequency
- Plan tetikleme "beklemede" state'ine work order koyar
- Bakım sıklığı 6 ayda bir: 20% verimleme sağlar (uyarı)

#### Yedek Parça
- Stok seviyesi reorder_level altına düştüğünde, auto satıcıya sipariş
- Tedarik süresi + 5 gün = warning threshold

---

## 6. ENTEGRASYON NOKTALARI

### 6.1 Harici Sistemler

#### IoT / Sensör Entegrasyonu
```
POST /api/v1/sensor-data
{
  "equipment_id": 1,
  "sensor_type": "temperature",
  "sensor_id": "SENS-001-TEMP",
  "value": 75.5,
  "unit": "°C",
  "timestamp": "2024-01-15T10:30:00Z"
}

Yanıt: {
  "status": "ok",
  "anomaly_detected": false,
  "anomaly_score": 0.15
}
```

#### ERP Entegrasyonu
- WorkOrder maliyetleri ERPX sistem muhasebesi ile sync
- Ekipman satın alma ve deprecated bilgileri sync
- Satıcı bilgileri ve fiyat güncelleme

#### SCADA/PLC Entegrasyonu
- Gerçek zamanlı ekipman durumu (operational/maintenance/error)
- Meter readings otomatik çekme
- Acil duruş bildirim

### 6.2 API Endpoints

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/v1/equipment` | Tüm ekipmanları listele |
| POST | `/api/v1/equipment` | Yeni ekipman ekle |
| GET | `/api/v1/equipment/<id>` | Ekipman detayları |
| GET | `/api/v1/equipment/<id>/kpi` | Ekipman KPI'ları |
| POST | `/api/v1/failures` | Yeni arıza raporu |
| GET | `/api/v1/failures?status=open` | Açık arızalar |
| POST | `/api/v1/work-orders` | Yeni iş emri |
| GET | `/api/v1/work-orders/<id>` | İş emri detayları |
| POST | `/api/v1/sensor-data` | Sensör verisi gönder |
| GET | `/api/v1/kpi/summary` | Genel KPI özeti |

---

## 7. RAPORLAMA VE ANALYTICS

### 7.1 Standart Raporlar

#### 1. Aylık Performans Raporu
- Dönem: Seçili ay
- Bileşenler:
  - Ortalama Kullanılabilirlik (%)
  - MTBF / MTTR (saat)
  - Toplam Arıza Sayısı
  - Toplam Bakım Maliyeti (€)
  - OEE
  - Yapılan İş Emri Sayısı
  - Tamamlama Yüzdesi
  - Top 5 Sık Arızalar

#### 2. EN 15341 Uyum Raporu
- Teknik Göstergeler (PO):
  - PO-MTBF: Mean Time Between Failures
  - PO-MTTR: Mean Time To Repair
  - PO-Availability: Kullanılabilirlik
- Maliyet Göstergeleri:
  - CM: Bakım Maliyeti
  - CM Ratio: Maliyet/Satın Alma Oranı
- Standardlara Uyum Durumu

#### 3. Ekipman Yaşam Döngüsü Raporu
- Ekipman: Seçili ekipman
- Bileşenler:
  - Satın alma tarihi ve maliyeti
  - Garansi durumu
  - Toplam İşletme Saati
  - Toplam Km / Döngü
  - Aşınma Seviyesi
  - Kalan Ömür Tahmini
  - Toplam Bakım Maliyeti
  - Depreciation Schedule

#### 4. İş Emri Analiz Raporu
- Dönem: Seçili (from-to)
- Metrikler:
  - Toplam İş Emri
  - Tamamlanan / Yapılmayan
  - Ortalama Tamamlama Süresi
  - Ortalama Maliyeti
  - Personel Verimliliği
  - Yedek Parça Kullanımı

#### 5. Personel Performans Raporu
- Teknisyen: Seçili
- Metrikler:
  - Tamamlanan İş Emri Sayısı
  - Ortalama Kalite Puanı
  - Beceri Seviyeleri
  - Müsaitlik %
  - Süresi Aşan Emirler

---

## 8. GÜVENLİK GEREKSINIMLERI

### 8.1 Kimlik Doğrulama ve Yetkilendirme
- **Authentication**: Flask-Login + session management
- **Password**: Werkzeug generate_password_hash + PBKDF2
- **Authorization**: Role-based access control (RBAC)
- **Session Timeout**: 30 dakika inaktivite
- **Password Policy**: Min 8 char, uppercase+lowercase+number required
- **Failed Login**: Max 5 başarısız deneme = 15 dk kilitli

### 8.2 Veri Güvenliği
- **Database**: SQLAlchemy ORM ile SQL injection önlemi
- **Data Encryption**: Hassas veriler enkripte (PyCryptodome)
  - Parola hash (PBKDF2)
  - Sensör kalibrasyonu parametreleri
- **Audit Trail**: Tüm kritik işlemler logger'a
- **Backup**: Günlük automated backup (encrypted)

### 8.3 Denetim ve Uyum
- **Audit Log**:
  - User, timestamp, action, affected_resource_id, old_value, new_value
  - Tutma süresi: 2 yıl
- **Compliance**:
  - ISO 27001: Erişim kontrol, veri şifreleme, backup
  - EN 13306: Bakım terminolojisi ve prosedürleri

### 8.4 API Güvenliği
- **Authentication**: Token-based (JWT) veya API key
- **Rate Limiting**: 100 req/minute per IP
- **Input Validation**: Whitelist pattern matching
- **Output Encoding**: XSS önlemi (HTML escaping)
- **HTTPS Only**: Production ortamında TLS 1.2+

---

## NOTLAR

- **Senaryo Güncelleme Sıklığı**: Yıllık
- **Veri Saklama**: 7 yıl (yasal gereksinim)
- **Yedekleme**: Günlük, 30 gün retention
- **Disaster Recovery**: RTO = 4 saat, RPO = 1 saat
- **Load Testing**: 500 concurrent users destekleme hedefi
