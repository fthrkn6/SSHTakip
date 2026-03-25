# HAFTA 4-12 İMPLEMENTASYON PLANI

## 🎯 Genel Bakış

Tüm beş büyük alanda başlangıç yapıları oluşturulmuştur. Her alan üzerinde paralel çalışma yapılabilir.

---

## 📂 YENİ DOSYALAR & YAPILARI

### 1. 🎨 UI/Frontend (utils_ui_config.py)
- **Bootstrap 5 Configuration**: Modern UI framework
- **Dark Mode Support**: Tema geçişi ve localStorage
- **Status Colors**: Equipment durumları için renkler
- **Health Check Pulse Animation**: Canlı sistem göstergesi
- **Responsive Design**: Mobile-first approach

**Sonraki Adımlar:**
```bash
# Bootstrap 5 upgrade
pip install Bootstrap==5.3.0

# Template güncellemeleri
# templates/ klasöründe tüm dosyalara ekle:
{% include 'layouts/dark_mode_toggle.html' %}

# Yeni dashboard widgets oluştur
# routes/dashboard.py → KPI cards, charts, status indicators
```

---

### 2. 📊 Advanced Reporting (utils_report_manager.py)
- **Report Templates**: 4 built-in templates (daily, weekly, monthly, FRACAS)
- **ReportTemplateManager**: Template management
- **ReportBuilder**: Report generation engine
- **Multi-format Export**: PDF, HTML, Excel, JSON

**Kullanım Örneği:**
```python
from utils_report_manager import template_manager, report_builder

# Template yükleme
template = template_manager.get_template('daily_ops')

# Rapor oluşturma
report = report_builder.build_report('daily_ops', filters={
    'date_range': 'today',
    'project_code': 'TRAM_001'
})

# Export etme
pdf_file = report_builder.export_to_format(report, 'pdf')
```

**Sonraki Adımlar:**
```bash
# ReportLab + Jinja2 template engine
pip install Jinja2 python-dateutil

# routes/reports.py genişlet
# Şablonları: templates/reports/
# PDF generation utility oluştur
```

---

### 3. ✅ Testing Framework (conftest.py, tests/ klasörü)

**Test Structure:**
```
tests/
├── __init__.py
├── test_models.py      # 23+ test methods
├── test_routes.py      # 20+ test methods
├── test_utils.py       # 25+ test methods
└── conftest.py         # Fixtures & configuration
```

**Test Coverage Durumu:**
- ✅ Models: 15 test cases
- ✅ Routes: 18 test cases
- ✅ Utils: 24 test cases
- ✅ Benchmarks: 3 performance tests
- **Target: 40% coverage (Week 4-5), 60% coverage (Week 6)**

**Çalıştırma:**
```bash
# Kurup test et
pytest tests/ -v

# Coverage raporu
pytest tests/ --cov=. --cov-report=html

# Background tests
pytest tests/ -m slow -v

# Specific test dosyası
pytest tests/test_models.py -v -k "test_user"
```

---

### 4. 🚀 Performance & Caching (utils_performance.py)

**Features:**
- **CacheManager**: Redis + Local fallback
- **Caching Decorators**: @cache_result, @invalidate_cache
- **Query Optimizer**: Eager loading helpers
- **AsyncTaskConfig**: Celery task definitions

**Entegrasyon:**
```python
from utils_performance import cache_manager, cache_result, CacheConfig

# Cache'i initialize et
from app import init_cache, cache_manager

# Function çıktısını cache'le
@cache_result(key_prefix='equipment', ttl=CacheConfig.TTL_HOUR)
def get_equipment_list(project_code):
    return Equipment.query.filter_by(project_code=project_code).all()

# Manual cache işlemleri
cache_manager.set('key', value, ttl=CacheConfig.TTL_MEDIUM)
result = cache_manager.get('key')
cache_manager.delete('key')
```

**Setup:**
```bash
# Redis kurulumu
docker run -d -p 6379:6379 redis:7-alpine

# Redis client kütüphanesi
pip install redis
```

---

### 5. 🔧 DevOps & Containerization

#### Dockerfile
- Multi-stage build (optimize edilmiş image)
- Health checks
- Non-root user (security)
- Production-ready gunicorn

#### docker-compose.yml
Services:
- **app**: Flask application (port 5000)
- **db**: PostgreSQL 15 (port 5432)
- **redis**: Redis caching (port 6379)
- **celery_worker**: Async task processor
- **nginx**: Reverse proxy (ports 80, 443)

**Başlat:**
```bash
# Build ve run
docker-compose up --build

# Production modunda
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
docker-compose -f docker-compose.yml up -d
```

#### GitHub Actions CI/CD (.github/workflows/ci-cd.yml)

Jobs:
1. **Code Quality**: black, isort, flake8, mypy
2. **Unit Tests**: pytest with coverage
3. **Security**: bandit, safety, pip-audit
4. **Build**: Docker image build & push
5. **Notify**: PR comments on failure

**Triggers:**
- Push to main/develop branches
- Pull requests

---

### 6. 🎯 Celery Async Tasks (celery_config.py)

**Tanımlı Tasks:**
- `generate_daily_report`: 18:00 her gün
- `sync_km_data`: Her 2 saatte
- `calculate_kpi`: 00:00 her gün
- `cleanup_old_data`: 01:00 her gün
- `send_maintenance_reminders`: 08:00 her gün

**Kullanım:**
```bash
# Worker başlat
celery -A celery_app worker --loglevel=info

# Beat scheduler başlat
celery -A celery_app beat --loglevel=info

# Monitoring (Flower)
celery -A celery_app flower
# Açık: http://localhost:5555
```

---

## 📅 HAFTALIK YÜKSEK SEVİYE PLAN

### HAFTA 4 - Temel Tasarı (Foundation)
**Hedef: Test framework + UI başlangıcı**

```
MON: Pytest setup & run initial tests
TUE: Model test coverage (KPI: 25%)
WED: Route test coverage (KPI: 20%)
THU: Utils test coverage (KPI: 20%)
FRI: Review & Bootstrap 5 update
```

- ✅ pytest conftest.py
- ✅ test_models.py: 23 test case
- ✅ test_routes.py: 20 test case
- ✅ test_utils.py: 25 test case
- ✅ CI/CD pipeline kurulu

**KPI: 30% coverage target**

---

### HAFTA 5 - UI/Reporting Gelişme
**Hedef: Modern UI + Report templates**

```
MON: Bootstrap 5 template migration
TUE: KPI dashboard widgets
WED: Report template system finalize
THU: PDF export with charts
FRI: Email scheduling (APScheduler)
```

**Deliverables:**
- Dashboard widgets (5+ cards)
- Report templates (4 tane)
- PDF export (reportlab integration)
- Email distribution

---

### HAFTA 6 - Performance & Testing Completion
**Hedef: 60% test coverage + caching**

```
MON: Redis caching integration
TUE-WED: Celery async tasks
THU: Query optimization
FRI: Performance testing & bottleneck analysis
```

**KPI: 60% coverage target**

---

### HAFTA 7-8 - Monitoring & Observability
**Hedef: Production-ready monitoring**

```
WK7:
- Sentry integration
- Log aggregation
- Health checks

WK8:
- Performance metrics
- Error tracking dashboard
- Alert configuration
```

---

### HAFTA 9-10 - Advanced Features
**Hedef: Feature completeness**

```
WK9:
- Advanced reporting filters
- Batch export operations
- API versioning

WK10:
- Scheduled report delivery
- Custom dashboards
- User preferences
```

---

### HAFTA 11-12 - Optimization & Deployment
**Hedef: Production deployment**

```
WK11:
- Load testing
- Database optimization
- Performance tuning

WK12:
- Security audit
- Deployment pipeline
- Documentation completion
```

---

## 🚀 BAŞLAMAK İÇİN

### Step 1: Environment Setup
```bash
# 1. Python env
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# 2. Dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-flask redis celery

# 3. Database
python reset_db.py  # or flask db upgrade

# 4. Environment variables
cp .env.example .env
# Edit .env and add SECRET_KEY, DATABASE_URL, etc.
```

### Step 2: Run Tests
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Watch mode (if installed)
pytest-watch tests/
```

### Step 3: Docker Setup
```bash
# Build & run all services
docker-compose up --build

# Check services
docker-compose ps

# View logs
docker-compose logs -f app
```

### Step 4: Start Development
```bash
# Development server
flask run

# With Redis and Celery (in separate terminals)
redis-server
celery -A celery_app worker
celery -A celery_app beat
```

---

## 📊 HEDEFLER & KPİLER

| Hafta | Module | Hedef | Metrik |
|-------|--------|-------|--------|
| 4 | Testing | Setup | 30% coverage |
| 5 | UI/Reporting | Features | 95% template completion |
| 6 | Performance | Optimization | 60% coverage |
| 7-8 | Monitoring | Production | 99% uptime |
| 9-10 | Advanced | Features | 100% API coverage |
| 11-12 | Deployment | Release | 0 critical bugs |

---

## 🔐 SECURITY CHECKLIST

- [ ] SECRET_KEY rotated regularly
- [ ] HTTPS/TLS enforced
- [ ] SQL injection prevention (SQLAlchemy parameterized queries)
- [ ] XSS protection (template escaping)
- [ ] CSRF tokens on forms
- [ ] Rate limiting (nginx + Flask-Limiter)
- [ ] Input validation
- [ ] Output encoding
- [ ] Dependency security scanning
- [ ] Regular penetration testing

---

## 📈 MONITORING & OBSERVABILITY

### Sentry Setup (Week 7)
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN'],
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1
)
```

### Logging
```python
from logging.handlers import RotatingFileHandler
import logging

# Configure rotating logs
handler = RotatingFileHandler('logs/app.log', maxBytes=10485760, backupCount=10)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
app.logger.addHandler(handler)
```

### Health Check Endpoint
```python
@app.route('/api/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'components': {
            'database': check_db(),
            'redis': check_redis(),
            'celery': check_celery()
        }
    }
```

---

## 🎓 KAYNAKLAR & DOCS

- **Flask**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **pytest**: https://docs.pytest.org/
- **Celery**: https://docs.celeryproject.io/
- **Docker**: https://docs.docker.com/
- **Redis**: https://redis.io/documentation
- **GitHub Actions**: https://docs.github.com/en/actions

---

## ❓ SORULAR?

Her hafta kuzeyde belirlenmiş kontrol noktaları var. Herhangi bir sorun veya engel yaşanırsa:
1. Logs kontrol et
2. Tests çalıştır
3. GitHub issues oluştur
4. Team collaboration slack'te sor

---

**Son Güncelleme:** 2026-03-25
**Version:** 1.0 - Implementation Ready
