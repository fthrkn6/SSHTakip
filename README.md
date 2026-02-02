# CMMS - Computerized Maintenance Management System

## 📋 Genel Bakış

Tren bakım yönetimi için kapsamlı, modüler ve ölçeklenebilir CMMS sistemi. 

### 🎯 Ana Hedefler (Madde 9-4-2-1)
- ✅ Bakım işlemlerinin tam izlenebilirliğini sağlama
- ✅ İnsan, malzeme ve finansal kaynakların yönetimini optimize etme
- ✅ Gerçek zamanlı izleme ve tahmine dayalı analiz
- ✅ Trenlerden toplanan verileri kullanarak proaktif bakım

### 📜 Standartlar ve Sertifikalar (Madde 9-4-2-2)
- **ISO 55000**: Varlık Yönetimi (Asset Management)
- **EN 15341**: Bakım Performans Göstergeleri (Maintenance KPI)
- **ISO 27001**: Siber Güvenlik ve Kritik Veri Koruma

## 🏗️ Teknik Mimari ve Birlikte Çalışabilirlik (Madde 9-4-3)

### Modüler Mimari (Madde 9-4-3-1)
- **Modüler Yapı**: Mevcut işlemleri kesintiye uğratmadan yeni modüller eklenebilir
- **Ölçeklenebilir Platform**: Açık teknoloji ve standart protokollerle uyumluluk
- **Flask-based Backend**: Python 3.13+ ile geliştirme
- **SQLite Database**: Üretimde PostgreSQL/MySQL'e geçiş hazır

### Bağlantı ve Entegrasyon (Madde 9-4-3-2)
- **Sensör Entegrasyonu**: Trenlerdeki sensörlerle gerçek zamanlı veri alımı
- **Dijital İkiz Desteği**: Tren sistemlerini modelleme ve simülasyon
- **IoT Protokolleri**: MQTT, REST API, WebSocket desteği
- **Harici Sistem Entegrasyonu**: ERP, MES, SCADA sistemleriyle uyumlu

### Kullanıcı Erişimi (Madde 9-4-3-3)
- **Rol Tabanlı Erişim**: Teknisyenler, yöneticiler, idareciler için güvenli erişim
- **Multi-Platform**: Web (PC, Tablet, Mobil) tam responsive tasarım
- **Saha Erişimi**: Mobil cihazlardan çevrimdışı çalışma desteği (planlı)

## ⚙️ Ayrıntılı Özellikler (Madde 9-4-4)

### 1. Ekipman Yönetimi (Madde 9-4-4-1)
- ✅ **Benzersiz Kodlama Sistemi**: Her tren, alt sistem ve parça için unique ID
- ✅ **Hiyerarşik Yapı**: Tren > Vagon > Alt Sistem > Bileşen
- ✅ **Teknik Doküman Erişimi**: Planlar, kılavuzlar, şemalar (doğrudan yazılımda)
- ✅ **Ekipman Durumu**: Operational, Maintenance, Repair, Decommissioned
- ✅ **Kritiklik Seviyeleri**: Low, Medium, High, Critical

### 2. Öngörücü ve Koşullu Bakım (Madde 9-4-4-2)
- ✅ **Makine Öğrenimi Algoritmaları**: Arıza tahmini (scikit-learn entegrasyonu)
- ✅ **Anomali Tespiti**: Sensör verilerinden otomatik sapma algılama
- ✅ **Otomatik Bildirimler**: Kritik anomaliler için anlık uyarılar
- ✅ **Eşik Bazlı Tetikleme**: Belirlenen parametrelerde otomatik iş emri

### 3. Gelişmiş Müdahale Planlaması (Madde 9-4-4-3)
- ✅ **Otomatik Plan Oluşturma**: Aşınma eşikleri ve kullanım durumuna göre
- ✅ **Önleyici Bakım Programları**: Periyodik ve koşul bazlı planlar
- ✅ **Müsaitlik Yönetimi**: Trenlerin kullanılamama durumlarının optimizasyonu
- ✅ **Operasyonel Etki Minimizasyonu**: Akıllı planlama algoritmaları

### 4. Kaynak Yönetimi (Madde 9-4-4-4)
- ✅ **Ekip Atama**: Beceri, kullanılabilirlik ve konuma göre teknisyen ataması
- ✅ **Maliyet İzleme**: İşçilik, parça, alet maliyetlerinin müdahale bazında takibi
- ✅ **Envanter Yönetimi**: Yedek parça stok takibi
- ✅ **Zaman Takibi**: Çalışma süresi ve verimlilik ölçümü

### 5. Anahtar Performans Göstergeleri - KPI (Madde 9-4-4-5)
- ✅ **MTBF**: Mean Time Between Failures (Ortalama Arıza Arası Süre)
- ✅ **MTTR**: Mean Time To Repair (Ortalama Onarım Süresi)
- ✅ **Kullanılabilirlik**: Availability hesaplaması
- ✅ **Güvenilirlik**: Reliability metrikleri
- ✅ **OEE**: Overall Equipment Effectiveness
- ✅ **İnteraktif Dashboard**: Genel ve özel performans göstergeleri
- ✅ **Otomatik Hesaplama**: Gerçek zamanlı KPI güncellemesi

### 6. İş Emri Yönetimi
- ✅ Otomatik iş emri oluşturma
- ✅ Önceliklendirme (critical, high, medium, low)
- ✅ Kaynak ve personel atama
- ✅ Durum takibi (pending, scheduled, in_progress, completed)
- ✅ Tamamlama notları ve onay mekanizması

### 7. Raporlama ve Dokümantasyon
- ✅ **PDF/Excel Export**: Tüm raporlar dışa aktarılabilir
- ✅ **Özelleştirilebilir Raporlar**: Dönem, ekipman, KPI bazlı filtreleme
- ✅ **Grafiksel Gösterimler**: Chart.js ile interaktif grafikler
- ✅ **Audit Trail**: Tüm işlemlerin tam kayıt altına alınması

### 8. Güvenlik ve Erişim Kontrolü
- ✅ **Rol Bazlı Erişim**: Admin, Manager, Technician, Operator
- ✅ **ISO 27001 Uyumlu**: Güvenlik politikaları ve şifreleme
- ✅ **Session Yönetimi**: Güvenli oturum kontrolü
- ✅ **Şifre Politikaları**: Hash'lenmiş parola saklama (Werkzeug)

### 9. API ve Entegrasyonlar
- ✅ **RESTful API**: Tüm modüller için tam API desteği
- ✅ **Sensör Veri API**: Real-time veri alımı endpoint'leri
- ✅ **Webhook Desteği**: Harici sistemlere bildirim
- ✅ **JSON Format**: Standart veri formatı
- Harici sistem entegrasyonları

## Kurulum

### Gereksinimler
- Python 3.8+
- PostgreSQL veya SQLite

### Adımlar

1. Virtual environment oluşturun:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

3. Environment değişkenlerini ayarlayın:
```bash
copy .env.example .env
# .env dosyasını düzenleyin
```

4. Veritabanını başlatın:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. İlk admin kullanıcısını oluşturun:
```python
from app import create_app, db
from models import User

app = create_app()
with app.app_context():
    admin = User(
        username='admin',
        email='admin@example.com',
        full_name='System Administrator',
        role='admin'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
```

6. Uygulamayı çalıştırın:
```bash
python app.py
```

Uygulama http://localhost:5000 adresinde çalışacaktır.

## Kullanım

### İlk Giriş
- Kullanıcı: `admin`
- Şifre: `admin123`

### Temel İş Akışı

1. **Ekipman Ekleme**: Ekipmanlar menüsünden yeni tren/bileşen ekleyin
2. **Bakım Planı Oluşturma**: Her ekipman için bakım planları tanımlayın
3. **İş Emri Yönetimi**: Otomatik veya manuel iş emirleri oluşturun
4. **Teknisyen Atama**: İş emirlerini uygun teknisyenlere atayın
5. **Bakım Kaydı**: Yapılan işlemleri kaydedin
6. **KPI İzleme**: Performans metriklerini takip edin

## API Kullanımı

### Ekipman Listesi
```bash
GET /api/v1/equipment
```

### Sensör Verisi Gönderme
```bash
POST /api/v1/sensor-data
{
    "equipment_id": 1,
    "sensor_type": "temperature",
    "value": 75.5,
    "unit": "°C"
}
```

### KPI Verileri
```bash
GET /api/v1/kpi/latest?equipment_id=1
```

## Teknoloji Stack

- **Backend**: Flask, SQLAlchemy
- **Frontend**: Bootstrap 5, Chart.js
- **Database**: SQLite / PostgreSQL
- **ML**: scikit-learn (öngörücü bakım)
- **Deployment**: Gunicorn

## Standartlar

- **ISO 55000**: Varlık yönetimi
- **EN 15341**: Bakım performans göstergeleri
- **ISO 27001**: Bilgi güvenliği

## Lisans

Proprietary - Tüm hakları saklıdır.

## Destek

Teknik destek için: support@example.com
