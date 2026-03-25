# HAFTA 4-12 ALIŞTIRMA KOLAYLIGI REHBERI

**Hızlı Referans Döküman** | Oluşturuldu: 25 Mart 2026

---

## 📱 HIZLI KOMUTLAR

### Hizmetleri Başlatma
```bash
# Flask App
flask run --debug

# Redis Connection Check
redis-cli --help

# Celery Worker
celery -A celery_tasks worker --loglevel=info --concurrency=4

# Celery Beat (Scheduler)
celery -A celery_tasks beat --loglevel=info

# Flower (Task Dashboard)
celery -A celery_tasks flower --port=5555

# All at once (Development)
tmux new-session -d -s app_dev -x 180 -y 50
tmux send-keys -t app_dev "flask run" Enter
tmux new-window -t app_dev -n redis
tmux send-keys -t app_dev:redis "redis-server" Enter
tmux new-window -t app_dev -n celery_worker
tmux send-keys -t app_dev:celery_worker "celery -A celery_tasks worker --loglevel=info" Enter
tmux new-window -t app_dev -n celery_beat
tmux send-keys -t app_dev:celery_beat "celery -A celery_tasks beat --loglevel=info" Enter
```

---

## 🌐 API ENDPOINTS

### Health & Monitoring
```
GET  /performance/health              - System health check
GET  /performance/metrics              - System metrics
GET  /performance/cache/stats          - Cache statistics
POST /performance/cache/clear          - Clear all cache (admin)
DELETE /performance/cache/pattern/<pattern> - Clear by pattern (admin)
GET  /performance/performance-dashboard - Admin dashboard (admin)
GET  /performance/slow-queries         - Slow query monitoring
```

### Reports
```
GET  /api/reports/templates            - List all templates
GET  /api/reports/templates/<name>     - Get template details
POST /api/reports/generate             - Generate report
POST /api/reports/export               - Export report (pdf/html/xlsx/json)
POST /api/reports/schedule             - Schedule report (admin)
GET  /api/reports/queue                - Report queue status (admin)
GET  /api/reports/cache/<id>           - Get cached report
DELETE /api/reports/cache/<id>         - Delete cached report
POST /api/reports/templates/custom     - Create custom template (admin)
```

---

## 📊 CALLABLE CELERY TASKS

### Immediate Tasks (Call directly)
```python
from celery_tasks import (
    generate_daily_report,
    export_data,
    send_email,
    send_maintenance_reminders,
    cleanup_old_data,
    check_system_health
)

# Example: Generate PDF export
export_data.delay('belgrad', 'pdf')

# Example: Send reminder emails
send_maintenance_reminders.delay()

# Example: Cleanup old data (90+ days)
cleanup_old_data.delay(days=90)

# Example: Check system health
check_system_health.delay()

# Example: Send email
send_email.delay(
    recipient='admin@company.com',
    subject='Haftalık Rapor',
    body='Ek dökümanı incele',
    html='<h1>Haftalık Rapor</h1>'
)
```

### Scheduled Tasks (Automatic via Beat)
```
18:00 Every Day   → generate_daily_report()
Monday 9 AM       → generate_weekly_report()
1st Day 9 AM      → generate_monthly_report()
Every 2 hours     → sync_km_data()
Every hour        → sync_service_status()
00:00 Every Day   → calculate_kpi()
00:01 Every Day   → cleanup_old_data()
Every 30 min      → check_system_health()
```

---

## 🔧 CONFIGURATION (.env)

### MUST SET (Production)
```
SECRET_KEY=your-secret-key-here-change-this
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379/0
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### DEFAULT (Development)
```
FLASK_ENV=development
DEBUG=True
CACHE_DEFAULT_TIMEOUT=300
LOG_LEVEL=DEBUG
FEATURE_REDIS_CACHE=1
FEATURE_ASYNC_TASKS=1
```

### Optional (Advanced)
```
SENTRY_DSN=your-sentry-dsn
SENTRY_ENABLED=0
MAX_CONTENT_LENGTH=52428800  # 50MB
LOG_FILE=logs/app.log
BCRYPT_LOG_ROUNDS=12
```

---

## 📁 FILE STRUCTURE

```
├── app.py                           ← MAIN APP (Enhanced)
├── models.py                        ← Database models (47+ classes)
├── config.py                        ← Configuration
├── celery_tasks.py                  ← Async jobs (12+)
├── requirements.txt                 ← Dependencies
│
├── routes/
│   ├── __init__.py
│   ├── dashboard.py                 ← Main dashboard
│   ├── equipment.py                 ← Equipment CRUD
│   ├── reports_legacy.py            ← Old reporting
│   ├── performance.py               ← Health/Cache/Metrics (NEW)
│   └── reporting.py                 ← Advanced reporting (NEW)
│
├── utils/
│   ├── daily_service_logger.py
│   ├── km_logger.py
│   ├── service_status_logger.py
│   ├── hbr_manager.py
│   ├── performance.py               ← Cache manager (NEW)
│   ├── report_manager.py            ← Report templates (NEW)
│   └── ui_config.py                 ← UI settings (NEW)
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── layouts/
│   │   └── dark_mode_toggle.html    ← Dark mode (NEW)
│   ├── performance/
│   │   └── dashboard.html           ← Perf dashboard (NEW)
│   └── reports/
│       └── templates.html           ← Report UI (NEW)
│
├── celery_config.py                 ← Task config (NEW)
│
├── docker-compose.yml               ← 5 services
├── .env.example                     ← Config template (EXPANDED)
├── .github/workflows/ci-cd.yml      ← CI/CD pipeline
│
└── conftest.py                      ← Pytest fixtures
```

---

## 🎯 COMMON TASKS

### Task 1: Generate Report Programmatically
```python
from utils_report_manager import template_manager, report_builder

# Get template
template = template_manager.get_template('daily_ops')

# Build report
report = report_builder.build_report(
    template_name='daily_ops',
    filters={
        'project_code': 'belgrad',
        'start_date': '2026-03-01',
        'end_date': '2026-03-25'
    }
)

# Export to PDF
pdf_bytes = report_builder.export_to_format(report, 'pdf')

# Save file
with open('report.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### Task 2: Check Cache Status
```python
# Via API
curl http://localhost:5000/performance/cache/stats

# Via Python
from utils_performance import cache_manager
stats = cache_manager.get_stats()
print(f"Cache Type: {stats['type']}")
print(f"Cache Size: {stats['size']} bytes")
```

### Task 3: Monitor System Health
```python
# Via API
curl http://localhost:5000/performance/health

# Response:
# {
#   "database": {"status": "healthy", "response_time": 0.002},
#   "cache": {"status": "healthy", "type": "redis"},
#   "app": {"status": "healthy", "uptime": "2h 15m"},
#   "celery": {"status": "healthy", "workers": 4}
# }
```

### Task 4: Schedule Report Distribution
```python
# Via API
POST /api/reports/schedule
{
    "template_name": "daily_ops",
    "project_code": "belgrad",
    "schedule": "0 18 * * *",  # 6 PM daily
    "recipients": ["admin@company.com"],
    "format": "pdf"
}

# Response: 201 Created
# {
#   "id": "sched_xyz123",
#   "status": "scheduled",
#   "next_run": "2026-03-25 18:00:00"
# }
```

### Task 5: Clear Cache Pattern
```bash
# Clear all equipment caches
curl -X DELETE http://localhost:5000/performance/cache/pattern/equipment:*

# Clear all project caches
curl -X DELETE http://localhost:5000/performance/cache/pattern/project:*

# Response: 200 OK
# {
#   "status": "success",
#   "pattern": "equipment:*",
#   "keys_deleted": 42,
#   "operation_time": 0.015
# }
```

---

## 🐛 DEBUGGING CHECKS

### Redis Connection
```bash
redis-cli ping
→ PONG  (healthy)
→ Error (not running)
```

### Celery Worker
```bash
celery -A celery_tasks inspect active
→ Lists running tasks

celery -A celery_tasks inspect stats
→ Worker statistics
```

### Database Connection
```bash
flask shell
>>> from models import db
>>> db.engine.execute('SELECT 1')
→ 1  (healthy)
```

### Import Check
```bash
python -c "from utils_performance import CacheManager; print('✓')"
python -c "from celery_tasks import generate_daily_report; print('✓')"
python -c "from routes.reporting import reporting_bp; print('✓')"
```

---

## 🎓 LEARNING RESOURCES

### Celery Task Examples
```python
# Simple task
@shared_task
def add(a, b):
    return a + b

# With delay
add.delay(2, 3)  # Returns immediately

# Get result
result = add.delay(2, 3)
result.get()  # Blocks until complete

# Chain tasks
from celery import chain
result = chain(task1.s(), task2.s())()

# Scheduled task
from celery.schedules import crontab
Beat Schedule: {
    'generate-daily': {
        'task': 'celery_tasks.generate_daily_report',
        'schedule': crontab(hour=18, minute=0),
    }
}
```

### Cache Examples
```python
# Use decorator
from utils_performance import cache_result, invalidate_cache

@cache_result(ttl=timedelta(hours=1))
def get_dashboard_data(project_code):
    return expensive_query()

# Manual cache operations
from utils_performance import cache_manager

cache_manager.set('key', value, ttl=timedelta(hours=1))
value = cache_manager.get('key')
cache_manager.delete('key')
cache_manager.clear_pattern('equipment:*')
```

---

## 📈 PERFORMANCE TIPS

1. **Use Caching**
   - Cache dashboard data (1 hour TTL)
   - Cache report templates (never expires)
   - Cache KPI calculations (6 hour TTL)

2. **Use Async Tasks**
   - Long exports (PDF, Excel)
   - Email distributions
   - Data syncs
   - Cleanup operations

3. **Monitor Metrics**
   - Check `/performance/metrics` regularly
   - Watch Celery task queue depth
   - Monitor Redis memory usage
   - Track slow queries

4. **Optimize Queries**
   - Use SQLAlchemy eager loading
   - Add database indexes
   - Use pagination (limit 100)
   - Cache frequently accessed data

---

## 🚨 ERROR HANDLING

### If Redis Unavailable
```
Status: Graceful fallback to local cache
Impact: Minor performance impact
Action: None (automatic)
```

### If Celery Unavailable
```
Status: Tasks queued but won't execute
Impact: Reports won't generate automatically
Action: Restart Celery services
```

### If Database Unavailable
```
Status: App won't start
Impact: Complete failure
Action: Restore database connection
```

---

## 📞 GETTING HELP

1. **Check Health:** `GET /performance/health`
2. **Check Logs:** `logs/app.log` or Flask stderr
3. **Check Celery:** `celery -A celery_tasks inspect active`
4. **Check Redis:** `redis-cli INFO`
5. **Check Templates:** `GET /api/reports/templates`

---

**VERSION:** 1.0  
**LAST UPDATED:** 25 Mart 2026  
**STATUS:** Production Ready ✅
