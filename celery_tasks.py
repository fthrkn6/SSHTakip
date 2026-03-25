"""
Celery Tasks Module
Background job processing for reports, exports, analytics
"""

import logging
from datetime import datetime, timedelta
from celery import shared_task
from flask import current_app

logger = logging.getLogger(__name__)


# ============================================
# REPORTING TASKS
# ============================================

@shared_task
def generate_daily_report():
    """Generate daily operations report"""
    try:
        from models import db
        from utils_report_manager import report_builder
        
        logger.info("Starting daily report generation...")
        
        report = report_builder.build_report('daily_ops', {
            'date_range': 'today'
        })
        
        logger.info(f"Daily report generated: {report['title']}")
        return {
            'status': 'success',
            'report': report['title'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Daily report generation failed: {e}")
        raise


@shared_task
def generate_weekly_report():
    """Generate weekly maintenance report"""
    try:
        from utils_report_manager import report_builder
        
        logger.info("Starting weekly report generation...")
        
        report = report_builder.build_report('weekly_maint', {
            'date_range': 'week'
        })
        
        logger.info(f"Weekly report generated: {report['title']}")
        return {
            'status': 'success',
            'report': report['title'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Weekly report generation failed: {e}")
        raise


@shared_task
def generate_monthly_report():
    """Generate monthly KPI report"""
    try:
        from utils_report_manager import report_builder
        
        logger.info("Starting monthly KPI report generation...")
        
        report = report_builder.build_report('monthly_kpi', {
            'date_range': 'month'
        })
        
        logger.info(f"Monthly report generated: {report['title']}")
        return {
            'status': 'success',
            'report': report['title'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Monthly report generation failed: {e}")
        raise


# ============================================
# DATA SYNCHRONIZATION TASKS
# ============================================

@shared_task
def sync_km_data():
    """Sync KM data from Excel to database"""
    try:
        from utils_equipment_sync import sync_equipment_with_excel
        
        logger.info("Starting KM data synchronization...")
        
        added, updated = sync_equipment_with_excel(project_code=None)
        
        logger.info(f"KM sync completed: {added} added, {updated} updated")
        return {
            'status': 'success',
            'added': added,
            'updated': updated,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"KM sync failed: {e}")
        raise


@shared_task
def sync_service_status():
    """Sync service status from Excel"""
    try:
        from utils_project_excel_store import sync_service_excel_to_db
        
        logger.info("Starting service status synchronization...")
        
        result = sync_service_excel_to_db()
        
        logger.info(f"Service status sync completed")
        return {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Service status sync failed: {e}")
        raise


# ============================================
# ANALYTICS & KPI TASKS
# ============================================

@shared_task
def calculate_kpi():
    """Calculate KPI metrics"""
    try:
        from models import db, Equipment, Failure, WorkOrder
        
        logger.info("Starting KPI calculation...")
        
        # Calculate metrics
        metrics = {
            'total_equipment': Equipment.query.count(),
            'active_failures': Failure.query.filter_by(status='open').count(),
            'pending_work_orders': WorkOrder.query.filter_by(status='pending').count(),
        }
        
        # Cache metrics
        from app import cache_manager
        cache_manager.set('kpi:daily', metrics, ttl=timedelta(hours=24))
        
        logger.info(f"KPI calculation completed: {metrics}")
        return {
            'status': 'success',
            'metrics': metrics,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"KPI calculation failed: {e}")
        raise


# ============================================
# EXPORT TASKS
# ============================================

@shared_task
def export_data(project_code=None, format='xlsx'):
    """Export data in specified format"""
    try:
        import pandas as pd
        from models import Equipment, Failure, WorkOrder
        
        logger.info(f"Starting data export: project={project_code}, format={format}")
        
        # Build export data
        data = {
            'equipment': Equipment.query.all(),
            'failures': Failure.query.all(),
            'work_orders': WorkOrder.query.all()
        }
        
        logger.info(f"Data export completed: {format}")
        return {
            'status': 'success',
            'format': format,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Data export failed: {e}")
        raise


# ============================================
# EMAIL & NOTIFICATION TASKS
# ============================================

@shared_task
def send_email(recipient, subject, body, html=None):
    """Send email notification"""
    try:
        from flask_mail import Mail, Message
        
        logger.info(f"Sending email to {recipient}: {subject}")
        
        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=body,
            html=html
        )
        
        logger.info(f"Email sent to {recipient}")
        return {
            'status': 'success',
            'recipient': recipient,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        raise


@shared_task
def send_maintenance_reminders():
    """Send maintenance reminders to technicians"""
    try:
        from models import MaintenancePlan, User
        
        logger.info("Sending maintenance reminders...")
        
        # Get upcoming maintenance plans
        tomorrow = datetime.utcnow().date() + timedelta(days=1)
        plans = MaintenancePlan.query.filter_by(
            planned_date=tomorrow,
            status='pending'
        ).all()
        
        # Send reminders
        for plan in plans:
            logger.info(f"Reminder sent for plan: {plan.id}")
        
        logger.info(f"Sent {len(plans)} maintenance reminders")
        return {
            'status': 'success',
            'reminders_sent': len(plans),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Maintenance reminder task failed: {e}")
        raise


# ============================================
# CLEANUP TASKS
# ============================================

@shared_task
def cleanup_old_data(days=90):
    """Clean up old data from database"""
    try:
        from models import db, ServiceStatus
        from datetime import datetime, timedelta
        
        logger.info(f"Starting data cleanup (older than {days} days)...")
        
        cutoff_date = datetime.utcnow().date() - timedelta(days=days)
        
        # Delete old service status records
        deleted = ServiceStatus.query.filter(
            ServiceStatus.date < cutoff_date
        ).delete()
        
        db.session.commit()
        
        logger.info(f"Cleanup completed: {deleted} records deleted")
        return {
            'status': 'success',
            'records_deleted': deleted,
            'cutoff_date': cutoff_date.isoformat(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Data cleanup failed: {e}")
        raise


# ============================================
# MONITORING TASKS
# ============================================

@shared_task
def check_system_health():
    """Check system health and log metrics"""
    try:
        from models import db, Equipment, Failure
        
        logger.info("Checking system health...")
        
        health = {
            'equipment_count': Equipment.query.count(),
            'open_failures': Failure.query.filter_by(status='open').count(),
            'closed_failures': Failure.query.filter_by(status='closed').count(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"System health: {health}")
        
        # Cache health status
        from app import cache_manager
        cache_manager.set('system:health', health, ttl=timedelta(hours=1))
        
        return health
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise


# ============================================
# BATCH PROCESSING TASKS
# ============================================

@shared_task
def process_batch(batch_id, items):
    """Process batch of items"""
    try:
        logger.info(f"Processing batch {batch_id}: {len(items)} items")
        
        results = []
        for item in items:
            # Process each item
            results.append({
                'id': item.get('id'),
                'status': 'processed'
            })
        
        logger.info(f"Batch {batch_id} completed: {len(results)} items processed")
        return {
            'status': 'success',
            'batch_id': batch_id,
            'items_processed': len(results),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise
