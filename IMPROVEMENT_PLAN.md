# 🚀 KAPSAMLI HIZLANDIRILMA VE İYİLEŞTİRME PLANI

## 🎯 Özet
Bu dokümanda projenin hızlanması ve kalitesinin arttırılması için yapılması gereken iyileştirmeler yer almaktadır.

---

## 🔴 KRİTİK PERFORMANS SORUNLARI (ACIL ÖNCELİK)

### 1. **GLOBAL SYNC MİDDLEWARE - EN BÜYÜK PROBLEM ⚠️**
**Dosya:** `app.py` (~satır 177)
**Problem:** Her request'te Excel dosyası okunup veritabanına yazılıyor
**Etki:** Page load = 2-5 saniye

**Çözüm (Seç biri):**
```python
# OPTION 1: Sync'i zaman temelli cache'le (KOLAY - 5 dakika)
from flask_caching import Cache
cache = Cache(app)

@app.before_request
@cache.cached(timeout=300)  # 5 dakika
def sync_excel_data():
    # Sync kodu
    pass

# OPTION 2: Background job yaparak yaz (ORTA - 20 dakika)
# Celery ile her 5 dakikada 1 kere çalıştır
from celery_tasks import sync_task

@celery.task
def sync_task():
    sync_equipment_with_excel()
    sync_service_excel_to_db()

# OPTION 3: Admin panelinden manuel sync et (ZOR - 30 dakika)
# Sync'i tamamen middleware'den çıkar
# Sadece admin isterse çalıştırabilsin

# TAVSIYE: Option 1 + 2'yi birlikte kullan
# Option 1: İlk 5 dakika cache'den de
# Option 2: Arka planda 5 dakikada 1 çalış
```

**Beklenen Hızlanma:** 2-5 saniye → 200-500ms ⭐ ÇOK ÖNEMLI

---

### 2. **DATABASE QUERY OPTİMİZASYONU**

**Problem:** N+1 query problemi, eager loading eksikliği

**Çözüm:**
```python
# BEFORE (N+1 problem)
failures = Failure.query.all()  # 1 query
for f in failures:
    print(f.equipment.code)  # +N query

# AFTER (Eager loading)
from sqlalchemy.orm import joinedload
failures = Failure.query.options(
    joinedload('equipment'),
    joinedload('rca_analysis')
).all()  # 1 query
```

**Yapılacaklar:**
- [ ] `models.py` tüm relationship'ler için eager loading ekle
- [ ] Sık kullanılan query'ler için helper fonksiyon yaz
- [ ] N+1 detection testi ekle

---

### 3. **DATABASE INDEXES EKSIK**

**Problem:** Sorgu yavaş çünkü indexed column yok

**Çözüm:**
```python
# models.py'de Model'in içine ekle
class Equipment(db.Model):
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    equipment_code = db.Column(db.String(50), unique=True, index=True)
    project_code = db.Column(db.String(50), index=True)  # ← EKLE
    tram_id = db.Column(db.String(50), index=True)      # ← EKLE
    
    __table_args__ = (
        db.Index('idx_equipment_project', 'project_code', 'equipment_code'),
        db.Index('idx_tram_search', 'tram_id', 'project_code'),
    )

class Failure(db.Model):
    __tablename__ = 'failures'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    fracas_id = db.Column(db.String(50), unique=True, index=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), index=True)
    project_code = db.Column(db.String(50), index=True)
    status = db.Column(db.String(20), index=True)
    
    __table_args__ = (
        db.Index('idx_failure_project_status', 'project_code', 'status'),
    )
```

**Gerekli Index'ler:**
- `Equipment.project_code`, `Equipment.equipment_code`
- `Failure.project_code`, `Failure.status`, `Failure.fracas_id`
- `WorkOrder.project_code`, `WorkOrder.status`
- `MaintenancePlan.equipment_id`, `MaintenancePlan.project_code`

---

## 📊 CACHING STRATEJİSİ (5-10 SEKİNDE HİZLANMA)

### Şu Anda:
- Local cache var ama kapsamlı değil

### Yapılacak:

```python
# utils_performance.py'yi genişlet
from utils_performance import cache_result, cache_manager
from datetime import timedelta

# 1. DASHBOARD VERİLERİ
@cache_result(key_prefix='dashboard', ttl=timedelta(minutes=5))
def get_dashboard_stats(project_code):
    """Dashboard için KPI hesapla"""
    return {
        'total_equipment': Equipment.query.filter_by(project_code=project_code).count(),
        'active_failures': Failure.query.filter_by(project_code=project_code, status='open').count(),
        'pending_orders': WorkOrder.query.filter_by(project_code=project_code, status='pending').count(),
    }

# 2. EKIPMAN LİSTESİ
@cache_result(key_prefix='equipment_list', ttl=timedelta(hours=1))
def get_equipment_list(project_code):
    """Project'in tüm ekipmanı"""
    return Equipment.query.filter_by(project_code=project_code).all()

# 3. KPI HESAPLAMASI
@cache_result(key_prefix='kpi', ttl=timedelta(hours=6))
def calculate_kpis(project_code, period='month'):
    """KPI'ları hesapla (ağır işlem)"""
    # MMTR, MTBF vs hesapla
    pass

# 4. AYARLAR
@cache_result(key_prefix='projects_config', ttl=timedelta(hours=24))
def get_projects_config():
    """projects_config.json yükleme"""
    with open('projects_config.json') as f:
        return json.load(f)

# 5. CACHE INVALIDATION
# Excel sync'den sonra ilgili cache'i temizle
def sync_equipment_with_excel():
    # ... sync kodu ...
    cache_manager.delete_pattern('equipment_list:*')
    cache_manager.delete_pattern('dashboard:*')
```

---

## ⚙️ PRODUCTION AYARLARI

### 1. **GUNICORN/UWSGI DEPLOYMENT**
```bash
# development
python app.py

# production (BU YAPILMALI!)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 --worker-class sync app:app

# veya uWSGI
pip install uwsgi
uwsgi --http :5000 --wsgi-file app.py --callable app --processes 4 --threads 2
```

### 2. **DATABASE CONNECTION POOLING**
```python
# app.py'de create_app() içine ekle
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'poolclass': QueuePool,
    'pool_size': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

### 3. **PostgreSQL'e Geçiş** (Opsiyonel ama tavsiye edilen)
```python
# SQLite => PostgreSQL
# Development: sqlite (hızlı)
# Production: PostgreSQL (robust)

import os
if os.getenv('ENV') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://user:pass@localhost/ssh_takip"
    )
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///ssh_takip.db'
    )
```

### 4. **REDIS CACHE (Production)**
```python
# requirements.txt'e ekle
redis==5.0.0
flask-caching==2.0.2

# app.py'de
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379')
})
```

---

## 🔧 KOD KALİTESİ IYILEŞTIRMELERI

### 1. **IMPORT OPTIMIZE ETMENİ**
```python
# ÜLTE (Her import etme)
from models import *  # ❌ BAD
from app import *     # ❌ BAD

# DOĞRU (Sadece gerekenleri import et)
from models import Equipment, Failure  # ✅ GOOD
from app import cache_manager         # ✅ GOOD
```

### 2. **MIDDLEWARE AZALT**
```python
# Şu anki sorun: çok fazla middleware
# Her biri page load'u yavaşlatan işlem yapıyor

# Kontrol et:
@app.before_request
def before_request():
    # Buraya yazılanları minimize et
    pass
```

### 3. **ERROR HANDLING**
```python
# try/except her yerde olmalı ama şu an bazı yerlerde eksik
# API endpoints'leri kontrol et

@bp.route('/api/equipment')
def get_equipment():
    try:
        equipment = Equipment.query.all()
        return jsonify([e.to_dict() for e in equipment]), 200
    except Exception as e:
        logger.error(f"Get equipment error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
```

### 4. **LOGGING AYARLARI**
```python
# Production'da çok fazla log yazılırsa yavaşlama olur
import logging
import os

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO')

# Development
logging.basicConfig(level=logging.DEBUG)

# Production
logging.basicConfig(level=logging.WARNING)
```

---

## 📈 PERFORMANS MONITORING

### 1. **Health Check Endpoint**
```
GET /performance/health
Response: 
{
  "status": "healthy",
  "database": {"status": "healthy", "records": 1234},
  "cache": {"status": "healthy"},
  "response_time_ms": 45
}
```

### 2. **Metrics Endpoint**
```
GET /performance/metrics
Response:
{
  "database": {
    "equipment": 156,
    "failures": 423,
    "work_orders": 89
  },
  "cache": {
    "type": "redis",
    "keys": 456,
    "memory_mb": 12.5
  }
}
```

### 3. **Slow Query Detection**
```python
# Örneği: utils_query_optimization.py'de var
# Admin panel'de /performance/slow-queries göster
```

---

## 🎯 HIZLI KAZANÇLAR (1-2 DAKİKA)

Bu işlemleri yapıp 20-30% hızlanma sağlayabilirsin:

```python
# 1. DEBUG MODE'u KAPAT
# .env'e ekle
FLASK_ENV=production
FLASK_DEBUG=0

# 2. JINJA2 OPTİMİZASYONLARU
app.jinja_env.cache = {}  # Template cache

# 3. GZIP COMPRESSION
from flask_compress import Compress
Compress(app)

# 4. CDN AYARLARI (Static files)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 yıl

# 5. RESPONSE HEADERS OPTIMIZE
@app.after_request
def add_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.cache_control.max_age = 3600
    return response
```

---

## 📋 YAPILACAKLAR LİSTESİ (SIRASINA GÖRE)

### Hafta 1 (ACIL - 20 SAATLİK İŞ)
- [ ] **Global sync'i cache'le (5 saat)**
  - Option 1: Basit cache implementation
  - Test: `pytest tests/test_sync_cache.py`
  
- [ ] **Database index'leri ekle (3 saat)**
  - Equipment, Failure, WorkOrder models
  - Migration oluştur
  
- [ ] **Caching decorator'ü genişlet (4 saat)**
  - 10+ sık query için cache ekle
  
- [ ] **Gunicorn setup (2 saat)**
  - docker-compose update
  - production.yml oluştur

- [ ] **PostgreSQL setup (3 saat)**
  - docker-compose'a DB service ekle
  - Connection string ayarla
  - SQLite'dan migration

### Hafta 2 (ÖNEMLİ - 15 SAATLİK İŞ)
- [ ] **N+1 query'leri fix'le (5 saat)**
  - Eager loading ekle
  - Test'leri yaz
  
- [ ] **Redis cache setup (4 saat)**
  - Docker'da Redis çalıştır
  - Flask-Caching entegre et
  
- [ ] **Performance monitoring (3 saat)**
  - Dashboard improve et
  - Metrics API'sı test et
  
- [ ] **Logging optimize et (3 saat)**
  - Log level'ı production'da azalt
  - Structured logging ekle

### Hafta 3 (OPTIONAL - 10 SAATLİK İŞ)
- [ ] **Code refactoring**
  - Utils organize et
  - Modularization
  
- [ ] **Frontend optimization**
  - JS/CSS minify
  - Image optimization
  
- [ ] **Load testing**
  - Apache JMeter veya locust
  - 100+ concurrent request test

---

## 💾 IMPLEMENTATION CHECKLIST

### Performance Fixes
```python
# 1. Cache Global Sync
# app.py'de ~line 177
# FROM: @app.before_request
# TO: @celery.task + @cache.cached()

# 2. Add Database Indexes
# models.py'e __table_args__ ekle

# 3. Eager Loading
# query.options(joinedload(...)) kullan

# 4. Connection Pooling
# SQLALCHEMY_ENGINE_OPTIONS ayarla

# 5. Gunicorn
# Startup script'i update et
```

### Code Quality
```python
# 1. Type Hints
# Fonksiyonlara type hints ekle

# 2. Docstrings
# Tüm fonksiyonlara docstring

# 3. Error Handling
# Try/except coverage: %90+

# 4. Logging
# INFO level'ı production'da WARNING'e düşür
```

---

## 📊 BEKLENEN SONUÇLAR

| Metrik | Şu Anki | Hedef | İyileştirme |
|--------|---------|-------|------------|
| Page Load | 2-5s | 0.5-1s | 75-80% ⭐ |
| API Response | 500-800ms | 100-200ms | 75% ⭐ |
| DB Query | 200-800ms | 50-150ms | 60% ⭐ |
| Cache Hit Rate | ~30% | 70%+ | +130% ⭐ |
| CPU Usage | 45-60% | 15-25% | -65% |
| Memory | 200MB | 150MB | -25% |

---

## 🛠️ TOOLS & RESOURCES

### Performance Testing
```bash
# Load test
pip install locust
locust -f locustfile.py --host=http://localhost:5000

# Profile
pip install py-spy
py-spy record -o profile.svg -- python app.py

# Query analysis
from utils_query_optimization import enable_query_profiling
enable_query_profiling(app)
```

### Monitoring
```bash
# Redis
docker run -d -p 6379:6379 redis:7

# PostgreSQL
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15
```

---

## 📚 Referanslar

- SQLAlchemy Performance: https://docs.sqlalchemy.org/en/20/faq/performance.html
- Flask Best Practices: https://flask.palletsprojects.com/en/2.3.x/bestpractices/
- Database Indexing: https://use-the-index-luke.com/
- Redis Caching: https://redis.io/docs/manual/client-side-caching/

---

**Hazırlayan:** Performance Analysis Agent
**Tarih:** 2026-03-28
**Durum:** 🟢 Hazır İmplementasyona

