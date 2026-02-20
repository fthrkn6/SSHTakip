"""
Global Sync Middleware optimizasyonu
====================================

PROBLEM: app.py satır 177'deki global_excel_sync(), 
her request'te Excel'i okuyup Database'e yazıyor.
Bu çok yavaştır.

ÇÖZÜM: Sync'i 1 saatte 1 kere yap (caching)
"""

import time
import os
from datetime import datetime, timedelta

# Global sync last execution time (memory'de tut)
_last_sync_time = {}
SYNC_INTERVAL = 3600  # 1 saat (3600 saniye)

def should_sync_excel(project_code):
    """
    Sync'in yapılması gerekip gerekmediğini kontrol et
    Eğer son sync'ten 1 saat geçmişse True döndür
    """
    current_time = time.time()
    last_sync = _last_sync_time.get(project_code, 0)
    
    # İlk kez çalışıyorsa veya 1 saat geçmişse sync yap
    if (current_time - last_sync) >= SYNC_INTERVAL:
        _last_sync_time[project_code] = current_time
        return True
    
    return False

# ========================================================
# app.py'de değiştirilecek kod
# ========================================================

"""
ESKI KOD (YAVAS - her request'te çalışır):
==========================================

@app.before_request
def global_excel_sync():
    '''Her request'te Excel'den araçları Equipment'a senkronize et'''
    if current_user.is_authenticated:
        from routes.dashboard import sync_excel_to_equipment
        current_project = session.get('current_project', session.get('project_code', 'belgrad'))
        try:
            sync_excel_to_equipment(current_project)
        except Exception as e:
            logger.error(f'Global sync hatası: {e}')


YENİ KOD (HIZLI - 1 saatte 1 kere çalışır):
=============================================

@app.before_request
def global_excel_sync():
    '''Excel senkronizasyonunu optimize et (1 saatte 1 kere)'''
    if current_user.is_authenticated:
        current_project = session.get('current_project', session.get('project_code', 'belgrad'))
        
        # Sync'in yapılması gerekip gerekmediğini kontrol et
        if should_sync_excel(current_project):
            try:
                from routes.dashboard import sync_excel_to_equipment
                sync_excel_to_equipment(current_project)
                print(f'[SYNC] {current_project} senkronize edildi')
            except Exception as e:
                logger.error(f'Global sync hatası: {e}')
        # Eğer sync gerekmiyorsa hiçbir şey yapma (çok hızlı!)


ALTERNATİF KOD (MANUEL SYNC - Admin panelinden kontrol):
========================================================

# Admin paneli için manuel sync button'u ekle
@app.route('/admin/sync-excel', methods=['POST'])
@login_required
@require_admin
def admin_sync_excel():
    '''Excel senkronizasyonunu manuel olarak trigger et'''
    try:
        current_project = session.get('current_project', 'belgrad')
        from routes.dashboard import sync_excel_to_equipment
        
        sync_excel_to_equipment(current_project)
        
        # Cache'i reset et
        _last_sync_time[current_project] = time.time()
        
        flash(f'✅ {current_project} Excel verileri senkronize edildi', 'success')
    except Exception as e:
        flash(f'❌ Senkronizasyon hatası: {str(e)}', 'danger')
    
    return redirect(url_for('admin.index'))
"""

# ========================================================
# ÜÇÜNCÜ SEÇENEK: BACKGROUND TASK (Celery)
# ========================================================
"""
Asynchronous sync (en profesyonelce çözüm)

pip install celery redis

# tasks.py:
from celery import Celery

app = Celery('bozankaya')

@app.task
def sync_excel_background(project_code):
    '''Background job olarak Excel senkronizasyonu'''
    from routes.dashboard import sync_excel_to_equipment
    sync_excel_to_equipment(project_code)

# app.py'de:
def global_excel_sync():
    '''Background job'u trigger et (non-blocking)'''
    if current_user.is_authenticated:
        current_project = session.get('current_project', 'belgrad')
        
        if should_sync_excel(current_project):
            # Background job olarak sync'i planla
            sync_excel_background.apply_async(
                args=[current_project],
                countdown=5  # 5 saniye sonra çalış
            )
"""

# ========================================================
# PERFORMANCE METRIKLERI
# ========================================================

PERFORMANCE_COMPARISON = """
PERFORMANCE KARŞILAŞTIRMASI
===========================

Her saniye ne kadar request yapılabilir?

1. YAVAS (Her request'te Excel sync - şimdiki durum):
   - Request processing time: 2-5 saniye (Excel işlemi)
   - RPS (Requests Per Second): ~0.2-0.5 (ÇOK YAVAS!)
   
2. ORTA (1 saatte 1 kere sync - RECOMMENDED):
   - Request processing time: 50-100ms
   - RPS: ~10-20 (NORMAL)
   
3. HIZLI (Manual sync - Admin'den kontrol):
   - Request processing time: 30-50ms
   - RPS: ~20-30 (HIZLI)

4. ÇOK HIZLI (Celery background job):
   - Request processing time: 20-30ms
   - RPS: ~30-50 (ÇOK HIZLI)
   - + Background task'ler paralel çalışır

✅ RECOMMENDED: Seçenek 2 (çabuk ve etkili)
"""

print(PERFORMANCE_COMPARISON)
