"""
Sayfa Yükleme Hızı Dedektörü
============================
Hangi sebebin yavaşlama yaptığını bulmak için
"""

import time
import logging
from functools import wraps

# Request timing decorator
def measure_request_time(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"📍 ROUTE: {f.__name__}")
        print(f"{'='*70}")
        
        try:
            result = f(*args, **kwargs)
            
            elapsed = time.time() - start_time
            
            # Renkle göster
            if elapsed < 0.2:
                status = f"⚡ HIZLI ({elapsed:.3f}s)"
            elif elapsed < 1.0:
                status = f"⚠️  ORTA ({elapsed:.3f}s)"
            else:
                status = f"🐢 YAVAS ({elapsed:.3f}s)"
            
            print(f"⏱️  {status}")
            print(f"{'='*70}\n")
            
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ HATA: {str(e)} ({elapsed:.3f}s)")
            print(f"{'='*70}\n")
            raise
    
    return decorated_function


# SQL Query timing (SQLAlchemy events)
def enable_query_logging(app, db):
    """Database sorgularının zamanını track et"""
    import logging
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    
    logging.basicConfig()
    logger = logging.getLogger('sqlalchemy.engine')
    
    # Önceki event'leri temizle
    for listener in event.contains(Engine, 'before_cursor_execute'):
        event.remove(Engine, 'before_cursor_execute', listener)
    for listener in event.contains(Engine, 'after_cursor_execute'):
        event.remove(Engine, 'after_cursor_execute', listener)
    
    query_times = {}
    
    @event.listens_for(Engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
        print(f"   🔵 SQL: {statement[:80]}...")
    
    @event.listens_for(Engine, "after_cursor_execute")
    def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info['query_start_time'].pop(-1)
        print(f"   ✓ Sorgu tamamlandı: {total:.4f}s")
        
        # Yavaş sorguları takip et
        if total > 0.1:
            print(f"   ⚠️  YAVAS SORGU: {total:.4f}s")


# Flask app'e timing middleware ekle
def add_timing_middleware(app):
    """Request/response zamanını ölç"""
    
    @app.before_request
    def before():
        app.request_start_time = time.time()
        from flask import request
        print(f"\n>>> {request.method} {request.path}")
    
    @app.after_request
    def after(response):
        elapsed = time.time() - app.request_start_time
        
        color = "⚡" if elapsed < 0.2 else "⚠️" if elapsed < 1.0 else "🐢"
        print(f"<<< {response.status_code} {color} {elapsed:.3f}s\n")
        
        return response


# ========================================================
# BROWSER'DA KONTROL ETMESI GEREKEN ŞEYLER
# ========================================================

BROWSER_CHECKS = """
1. DEVELOPER TOOLS AÇMA (F12)
   
   a) Performance tab:
      - Sayfa açma süresi
      - Network gecikmesi
   
   b) Network tab:
      - Hangi file'lar yavaş yükleniyor?
      - CSS/JS boyutları
      - Requests sayısı

2. CONSOLE TAB:
   - JavaScript hatası var mı?
   - Loading mesajları

3. TIMING ETKİLİ SAYFALAR:
   - Dashboard
   - Bakım Planları
   - Arıza Listesi
   - Servis Durumu
"""

# ========================================================
# OLASI SEBEPLERLE ÇÖZÜMLERİ
# ========================================================

SLOWNESS_CAUSES = """
🐢 SAYFA YÜKLEME YAVASLIĞI - SEBEPLERİ

1. ⏱️ SERVER YAVAŞ RESPONSE
   ├─ Sebebi: Database sorguları yavaş
   └─ Çözüm: Database index'ı ekle, query'i optimize et
   
   ├─ Sebebi: Excel dosyası okunuyor
   └─ Çözüm: Excel'i cache'le veya asynchronous işle
   
   ├─ Sebebi: Global sync middleware her request'te çalışıyor
   └─ Çözüm: ✅ YAPILDI (1 saatte 1 kere)

2. 📦 BÜYÜK BROWSER CACHE
   ├─ Sebebi: CSS/JS boyutu fazla
   └─ Çözüm: Minify et, CDN kullan
   
   ├─ Sebebi: Resim boyutu fazla
   └─ Çözüm: WebP format, compression

3. 🌐 NETWORK GECIKMESI
   ├─ Sebebi: Çok sayıda request
   └─ Çözüm: Bundle'la, HTTP/2 kullan

4. 💾 DATABASE LOCK (SQLite)
   ├─ Sebebi: SQLite concurrent request'lere zayıf
   └─ Çözüm: PostgreSQL'e migrate et

5. 🔄 DEBUG MODE AÇIK
   ├─ Sebebi: Flask debug=True açık
   └─ Çözüm: ✅ YAPILDI (FLASK_ENV=production)
"""

print(BROWSER_CHECKS)
print(SLOWNESS_CAUSES)
