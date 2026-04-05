"""
Scheduled Tasks - APScheduler ile periyodik görevler
Redis/Celery gerektirmez, Flask app içinde çalışır.
"""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

scheduler = None


def init_scheduler(app):
    """APScheduler'ı Flask app ile başlat"""
    global scheduler
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()
        
        # Günlük rapor: her gün 18:00
        scheduler.add_job(
            func=lambda: _run_with_app(app, generate_daily_summary),
            trigger='cron', hour=18, minute=0,
            id='daily_summary', replace_existing=True
        )
        
        # Bakım hatırlatma: her gün 08:00
        scheduler.add_job(
            func=lambda: _run_with_app(app, check_maintenance_reminders),
            trigger='cron', hour=8, minute=0,
            id='maintenance_reminders', replace_existing=True
        )
        
        # KPI hesaplama: gece yarısı
        scheduler.add_job(
            func=lambda: _run_with_app(app, calculate_daily_kpi),
            trigger='cron', hour=0, minute=5,
            id='daily_kpi', replace_existing=True
        )
        
        scheduler.start()
        logger.info("Scheduler initialized with %d jobs", len(scheduler.get_jobs()))
    except ImportError:
        logger.warning("APScheduler not installed - scheduled tasks disabled")
    except Exception as e:
        logger.warning(f"Scheduler init failed: {e}")


def _run_with_app(app, func):
    """Flask app context içinde çalıştır"""
    with app.app_context():
        try:
            func()
        except Exception as e:
            logger.error(f"Scheduled task error in {func.__name__}: {e}")


def generate_daily_summary():
    """Günlük özet - açık arıza ve iş emri sayıları"""
    from models import Failure, WorkOrder
    
    open_failures = Failure.query.filter_by(status='acik').count()
    in_progress = Failure.query.filter_by(status='devam_ediyor').count()
    pending_orders = WorkOrder.query.filter_by(status='beklemede').count()
    
    logger.info(
        f"[DAILY SUMMARY] Açık arıza: {open_failures}, "
        f"Devam eden: {in_progress}, Bekleyen iş emri: {pending_orders}"
    )


def check_maintenance_reminders():
    """Bakım hatırlatmalarını kontrol et ve bildirim oluştur"""
    from models import db, Equipment, Notification, User
    
    # Bakım eşiğine yaklaşan ekipmanları bul
    equipments = Equipment.query.filter(
        Equipment.km_threshold > 0,
        Equipment.status == 'aktif'
    ).all()
    
    admin_users = User.query.filter_by(role='admin').all()
    admin_ids = [u.id for u in admin_users]
    
    for eq in equipments:
        km_since = eq.current_km - eq.last_km_at_maintenance
        if eq.km_threshold > 0 and km_since >= eq.km_threshold * 0.9:
            for uid in admin_ids:
                existing = Notification.query.filter_by(
                    user_id=uid, title=f'Bakım hatırlatma: {eq.equipment_code}',
                    is_read=False
                ).first()
                if not existing:
                    n = Notification(
                        user_id=uid,
                        title=f'Bakım hatırlatma: {eq.equipment_code}',
                        message=f'{eq.name} - KM eşiğine yaklaşıyor ({km_since}/{eq.km_threshold} km)',
                        category='warning'
                    )
                    db.session.add(n)
    db.session.commit()
    logger.info("[MAINTENANCE CHECK] Completed")


def calculate_daily_kpi():
    """Günlük KPI hesapla"""
    from models import Failure, ServiceStatus
    
    today = datetime.utcnow().strftime('%Y-%m-%d')
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Dünkü arıza sayısı
    failures_yesterday = Failure.query.filter(
        Failure.failure_date >= yesterday,
        Failure.failure_date < today
    ).count()
    
    # Dünkü servis durumu
    in_service = ServiceStatus.query.filter_by(
        date=yesterday, status='Servis'
    ).count()
    out_of_service = ServiceStatus.query.filter_by(
        date=yesterday, status='Servis Dışı'
    ).count()
    
    total = in_service + out_of_service
    availability = (in_service / total * 100) if total > 0 else 0
    
    logger.info(
        f"[DAILY KPI] {yesterday} - Arıza: {failures_yesterday}, "
        f"Availability: {availability:.1f}% ({in_service}/{total})"
    )
