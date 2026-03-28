# 🎯 HAZIR KOD DEĞİŞİKLİKLERİ - COPY-PASTE YAPILABILIR

## Dosya 1: models.py - Database Indexes Ekle

### CHANGE 1: Equipment Model'ine Index Ekle
**Nerede:** `models.py`, Equipment class tanımı
**Ne:** Index'ler ekle - sorguları hızlandır

```python
# ESKI HALKA BUNU DEĞİŞTİR:

class Equipment(db.Model):
    """Ekipman modeli"""
    __tablename__ = 'equipment'
    # ... column definitions ...

# YENİ HAL:

class Equipment(db.Model):
    """Ekipman modeli"""
    __tablename__ = 'equipment'
    # ... column definitions ...
    
    # Equipment code index et
    equipment_code = db.Column(db.String(50), unique=True, index=True)
    
    # Project code index et
    project_code = db.Column(db.String(50), index=True)
    
    # Tram ID index et
    tram_id = db.Column(db.String(50), index=True)
    
    # Composite indexes
    __table_args__ = (
        db.Index('idx_equipment_project', 'project_code', 'equipment_code'),
        db.Index('idx_tram_lookup', 'tram_id', 'project_code'),
    )
```

### CHANGE 2: Failure Model'ine Index Ekle
```python
# ESKI HAL:
class Failure(db.Model):
    """Arıza modeli"""
    __tablename__ = 'failures'
    # ... columns ...

# YENİ HAL:
class Failure(db.Model):
    """Arıza modeli"""
    __tablename__ = 'failures'
    # ... columns ...
    
    # Indexes
    __table_args__ = (
        db.Index('idx_failure_fracas', 'fracas_id'),
        db.Index('idx_failure_equipment', 'equipment_id'),
        db.Index('idx_failure_project_status', 'project_code', 'status'),
    )
```

### CHANGE 3: WorkOrder Model'ine Index Ekle
```python
# ESKI HAL:
class WorkOrder(db.Model):
    """İş emri modeli"""
    __tablename__ = 'work_orders'
    # ... columns ...

# YENİ HAL:
class WorkOrder(db.Model):
    """İş emri modeli"""
    __tablename__ = 'work_orders'
    # ... columns ...
    
    # Indexes
    __table_args__ = (
        db.Index('idx_workorder_project_status', 'project_code', 'status'),
        db.Index('idx_workorder_equipment', 'equipment_id'),
    )
```

---

## Dosya 2: routes/api.py - Caching Ekle

### CHANGE 1: Header'a cache import ekle
**Nerede:** `routes/api.py` içinde, imports bölümü

```python
# ÖYA IMPORTS:
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Equipment, Failure
import logging
from typing import Dict, Any
from datetime import datetime

# YENİ HAL:
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Equipment, Failure
import logging
from typing import Dict, Any
from datetime import datetime, timedelta  # ← EKLE timedelta

# Utils'den import et
try:
    from utils_performance import cache_result
except ImportError:
    # Cache yoksa dummy decorator
    def cache_result(key_prefix, ttl=None):
        def decorator(f):
            return f
        return decorator
```

### CHANGE 2: projects() fonksiyonuna cache ekle
**Nerede:** `/api/projects` endpoint'i

```python
# ÖYA:
@bp.route('/projects', methods=['GET'])
@login_required
def projects() -> Dict[str, Any]:
    """Get user's accessible projects"""
    # ... code ...

# YENİ:
@bp.route('/projects', methods=['GET'])
@login_required
@cache_result(key_prefix='api:projects', ttl=timedelta(hours=24))
def projects() -> Dict[str, Any]:
    """Get user's accessible projects"""
    # ... code ...
```

### CHANGE 3: failure_by_fracas_id() fonksiyonuna cache ekle
```python
# ÖYA:
@bp.route('/failure-by-fracas-id', methods=['GET'])
@login_required
def failure_by_fracas_id() -> Dict[str, Any]:
    """Get failure by FRACAS ID"""
    # ... code ...

# YENİ:
@bp.route('/failure-by-fracas-id', methods=['GET'])
@login_required
@cache_result(key_prefix='api:failure:fracas', ttl=timedelta(hours=12))
def failure_by_fracas_id() -> Dict[str, Any]:
    """Get failure by FRACAS ID"""
    # ... code ...
```

### CHANGE 4: equipment_parts() fonksiyonuna cache ekle
```python
# ÖYA:
@bp.route('/equipment-parts', methods=['GET'])
@login_required
def equipment_parts() -> Dict[str, Any]:
    """Lookup spare parts by equipment"""
    # ... code ...

# YENİ:
@bp.route('/equipment-parts', methods=['GET'])
@login_required
@cache_result(key_prefix='api:equipment:parts', ttl=timedelta(hours=6))
def equipment_parts() -> Dict[str, Any]:
    """Lookup spare parts by equipment"""
    # ... code ...
```

### CHANGE 5: statistics() fonksiyonuna cache ekle
```python
# ÖYA:
@bp.route('/statistics/<statistic_type>', methods=['GET'])
@login_required
def statistics(statistic_type: str) -> Dict[str, Any]:
    """Get statistics by type"""
    # ... code ...

# YENİ:
@bp.route('/statistics/<statistic_type>', methods=['GET'])
@login_required
@cache_result(key_prefix='api:statistics', ttl=timedelta(hours=1))
def statistics(statistic_type: str) -> Dict[str, Any]:
    """Get statistics by type"""
    # ... code ...
```

---

## Dosya 3: routes/api.py - Eager Loading Ekle

### CHANGE 6: equipment_parts() için eager loading
```python
# ÖYA:
@bp.route('/equipment-parts', methods=['GET'])
@login_required
@cache_result(key_prefix='api:equipment:parts', ttl=timedelta(hours=6))
def equipment_parts() -> Dict[str, Any]:
    """Lookup spare parts by equipment"""
    try:
        equipment_code = request.args.get('equipment_code')
        
        if not equipment_code:
            return jsonify({'error': 'equipment_code required'}), 400
        
        equipment = Equipment.query.filter_by(equipment_code=equipment_code).first()
        # ... rest of code ...

# YENİ:
@bp.route('/equipment-parts', methods=['GET'])
@login_required
@cache_result(key_prefix='api:equipment:parts', ttl=timedelta(hours=6))
def equipment_parts() -> Dict[str, Any]:
    """Lookup spare parts by equipment"""
    try:
        equipment_code = request.args.get('equipment_code')
        
        if not equipment_code:
            return jsonify({'error': 'equipment_code required'}), 400
        
        # EAGER LOADING EKLE - ← BU LİNE
        from sqlalchemy.orm import joinedload
        
        equipment = Equipment.query.filter_by(
            equipment_code=equipment_code
        ).options(
            joinedload('spare_parts')  # İlişkili yedek parçaları önceden yükle
        ).first()
        # ... rest of code ...
```

---

## Dosya 4: routes/dashboard.py - Cache Invalidation

### CHANGE 7: sync_excel_to_equipment() sonuna cache clear ekle

**Nerede:** `routes/dashboard.py`, `sync_excel_to_equipment()` fonksiyonunun sonunda

```python
# ÖYA (fonksiyonun sonu):
def sync_excel_to_equipment(current_project):
    """Excel'den veriyi ekipmanlara senkron et"""
    # ... lots of sync code ...
    logger.info(f"Senkronizasyon tamamlandı: {current_project}")
    return synced_count

# YENİ (cache clearing ekle):
def sync_excel_to_equipment(current_project):
    """Excel'den veriyi ekipmanlara senkron et"""
    # ... lots of sync code ...
    logger.info(f"Senkronizasyon tamamlandı: {current_project}")
    
    # ← BURAYA EKLE: Cache'i temizle
    try:
        from app import cache_manager
        cache_manager.delete_pattern('api:*')
        cache_manager.delete_pattern('equipment*')
        cache_manager.delete_pattern('dashboard*')
        logger.info(f"Cache temizlendi: {current_project}")
    except Exception as cache_error:
        logger.warning(f"Cache temizleme hatası: {cache_error}")
    
    return synced_count
```

---

## Dosya 5: app.py - Compression & Headers Optimize

### CHANGE 8: Performance headers ekle

**Nerede:** `app.py`, `create_app()` fonksiyonunda, cache headers bölümü

```python
# ÖYA:
@app.after_request
def add_cache_headers(response):
    """Add cache control headers to prevent browser caching of HTML/templates"""
    if response.content_type and ('text/html' in response.content_type or 'application/json' in response.content_type):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# YENİ:
@app.after_request
def add_cache_headers(response):
    """Add cache control headers to prevent browser caching of HTML/templates"""
    if response.content_type and ('text/html' in response.content_type or 'application/json' in response.content_type):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    # Static files (CSS, JS, images) için 1 yıl cache
    if response.content_type and any(x in response.content_type for x in ['text/css', 'application/javascript', 'image/']):
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    
    return response
```

---

## 🔍 DATABASE INDEX KONTROLÜ

### SQLite Index'leri Kontrol Et
```sql
-- Terminal'de çalıştır:
sqlite3 ssh_takip_bozankaya.db

-- Tüm index'leri listele:
.indices

-- Spesifik table için:
.indices equipment
.indices failures
.indices work_orders

-- Sonra:
.quit
```

### Eksik Index'leri Oluştur (Manuel SQL)
```sql
-- Eğer index yoksa, aşağıdıyapıştır:

CREATE INDEX IF NOT EXISTS idx_equipment_code ON equipment(equipment_code);
CREATE INDEX IF NOT EXISTS idx_equipment_project ON equipment(project_code, equipment_code);
CREATE INDEX IF NOT EXISTS idx_tram_lookup ON equipment(tram_id, project_code);

CREATE INDEX IF NOT EXISTS idx_failure_fracas ON failures(fracas_id);
CREATE INDEX IF NOT EXISTS idx_failure_equipment ON failures(equipment_id);
CREATE INDEX IF NOT EXISTS idx_failure_project_status ON failures(project_code, status);

CREATE INDEX IF NOT EXISTS idx_workorder_project_status ON work_orders(project_code, status);
CREATE INDEX IF NOT EXISTS idx_workorder_equipment ON work_orders(equipment_id);
```

---

## ✅ UYGULAMA KONTROL LİSTESİ

```
[ ] 1. models.py'e indexes ekle (Equipment, Failure, WorkOrder)
[ ] 2. Database migrate et (migration veya manual SQL)
[ ] 3. routes/api.py'e cache decorators ekle (5 fonksiyon)
[ ] 4. routes/dashboard.py'e cache invalidation ekle
[ ] 5. app.py'ye performance headers ekle
[ ] 6. Uygulamayı test et:
    [ ] npm run dev (veya python app.py)
    [ ] Browser DevTools Network tab'ında kontrol et
    [ ] Cache temizle → sayfa yükleme zamanı kontrol et
    [ ] 2. yüklemede daha hızlı olmalı
[ ] 7. Metrics kontrol et: /performance/metrics
```

---

## 🧪 QUICK TEST SCRIPT

`test_perf_changes.py` oluştur:

```python
import time
import requests
from datetime import datetime

BASE_URL = "http://localhost:5000"

# Login headers (eğer gerekirse)
headers = {'User-Agent': 'Performance Tester'}

endpoints = [
    '/api/projects',
    '/api/statistics/equipment',
    '/api/statistics/failures',
]

print("🚀 Performance Test Başlandı")
print("=" * 60)

for endpoint in endpoints:
    print(f"\n📊 Testing: {endpoint}")
    
    # 1. İlk çalışma (cache yok)
    start = time.time()
    r1 = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
    time1 = time.time() - start
    print(f"  1. Çağrı (no cache): {time1*1000:.0f}ms")
    
    # 2. İkinci çalışma (cache'den)
    start = time.time()
    r2 = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
    time2 = time.time() - start
    print(f"  2. Çağrı (cached):   {time2*1000:.0f}ms")
    
    hizlanma = ((time1 - time2) / time1 * 100) if time1 > 0 else 0
    print(f"  ⚡ Hızlanma: {hizlanma:.1f}%")
    
    if time2 < time1 * 0.8:
        print(f"  ✅ BAŞARILI - Cache çalışıyor!")
    else:
        print(f"  ⚠️ Cache çalışmıyor olabilir")

print("\n" + "=" * 60)
print("✅ Test tamamlandı")
```

**Çalıştır:**
```bash
python -m pip install requests
python test_perf_changes.py
```

---

## 📈 BEKLENEN SONUÇ METFORSLARI

```
BEFORE:
  1. Çağrı: 450ms
  2. Çağrı: 420ms
  ⚡ Hızlanma: 7%  (Cache yok)

AFTER:
  1. Çağrı: 450ms
  2. Çağrı: 25ms
  ⚡ Hızlanma: 94%  ✅ BAŞARILI!
```

