"""
Celery Configuration for Async Task Processing
Configure background job processing with Redis
"""

import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def make_celery(app=None):
    """
    Initialize Celery with Flask app
    
    Usage:
        from app import create_app
        app = create_app()
        celery = make_celery(app)
    """
    app = app or create_app()
    
    celery = Celery(
        app.import_name,
        backend=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )
    
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery


# Celery Configuration
class CeleryConfig:
    """Celery configuration"""
    
    # Broker and Backend
    broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # Task Configuration
    task_serializer = 'json'
    accept_content = ['json']
    result_serializer = 'json'
    timezone = 'UTC'
    enable_utc = True
    
    # Task Execution
    task_track_started = True
    task_time_limit = 30 * 60  # 30 minute hard time limit
    task_soft_time_limit = 25 * 60  # 25 minute soft time limit
    
    # Worker Configuration
    worker_prefetch_multiplier = 1
    worker_max_tasks_per_child = 100
    
    # Retry Configuration
    task_autoretry_for = (Exception,)
    task_max_retries = 3
    task_default_retry_delay = 60  # Retry after 60 seconds
    
    # Result Configuration
    result_expires = 3600  # Results expire after 1 hour
    result_extended = True
    result_backend_transport_options = {
        'master_name': 'mymaster'
    }
    
    # Beat Schedule (Periodic Tasks)
    beat_schedule = {
        'generate-daily-report': {
            'task': 'tasks.generate_daily_report',
            'schedule': crontab(hour=18, minute=0),  # 6 PM daily
        },
        'sync-km-data': {
            'task': 'tasks.sync_km_data',
            'schedule': crontab(hour='*/2'),  # Every 2 hours
        },
        'calculate-kpi': {
            'task': 'tasks.calculate_kpi',
            'schedule': crontab(hour=0, minute=0),  # Midnight daily
        },
        'cleanup-old-data': {
            'task': 'tasks.cleanup_old_data',
            'schedule': crontab(hour=1, minute=0),  # 1 AM daily
        },
        'send-maintenance-reminders': {
            'task': 'tasks.send_maintenance_reminders',
            'schedule': crontab(hour=8, minute=0),  # 8 AM daily
        },
    }


# Task Definitions
# Create app and celery instance first:
# from app import create_app, celery
# 
# @celery.task
# def async_task(param1, param2):
#     """Example async task"""
#     return f"Result: {param1} {param2}"

TASK_CONFIGS = {
    'generate_daily_report': {
        'priority': 'high',
        'timeout': 600,  # 10 minutes
        'queue': 'high_priority',
        'rate_limit': '1/m',  # 1 per minute
    },
    'generate_report': {
        'priority': 'high',
        'timeout': 1800,  # 30 minutes
        'queue': 'high_priority',
    },
    'export_data': {
        'priority': 'medium',
        'timeout': 1200,  # 20 minutes
        'queue': 'default',
    },
    'send_email': {
        'priority': 'low',
        'timeout': 300,  # 5 minutes
        'queue': 'low_priority',
    },
    'sync_km_data': {
        'priority': 'medium',
        'timeout': 600,  # 10 minutes
        'queue': 'default',
        'rate_limit': '1/h',  # 1 per hour
    },
    'analyze_failure': {
        'priority': 'high',
        'timeout': 900,  # 15 minutes
        'queue': 'high_priority',
    },
    'calculate_kpi': {
        'priority': 'medium',
        'timeout': 1800,  # 30 minutes
        'queue': 'default',
        'rate_limit': '1/d',  # 1 per day
    },
    'cleanup_old_data': {
        'priority': 'low',
        'timeout': 3600,  # 1 hour
        'queue': 'low_priority',
    },
}


# Task Monitoring Helper
class TaskMonitor:
    """Monitor Celery task execution"""
    
    @staticmethod
    def get_active_tasks(celery):
        """Get active tasks"""
        return celery.control.inspect().active()
    
    @staticmethod
    def get_scheduled_tasks(celery):
        """Get scheduled tasks"""
        return celery.control.inspect().scheduled()
    
    @staticmethod
    def get_registered_tasks(celery):
        """Get registered tasks"""
        return celery.control.inspect().registered()
    
    @staticmethod
    def get_task_stats(celery):
        """Get worker stats"""
        return celery.control.inspect().stats()


# Task Helpers
def queue_task(celery, task_name, *args, **kwargs):
    """Queue a task for execution"""
    try:
        config = TASK_CONFIGS.get(task_name, {})
        
        # Get the task function
        task_func = celery.tasks.get(f'tasks.{task_name}')
        
        if task_func:
            # Apply task with configuration
            result = task_func.apply_async(
                args=args,
                kwargs=kwargs,
                queue=config.get('queue', 'default'),
                priority=config.get('priority', 'medium'),
                timeout=config.get('timeout', 300),
            )
            
            logger.info(f"Task queued: {task_name} (ID: {result.id})")
            return result
        else:
            logger.error(f"Task not found: {task_name}")
            return None
    
    except Exception as e:
        logger.error(f"Failed to queue task {task_name}: {e}")
        return None


def get_task_status(celery, task_id):
    """Get status of a task"""
    try:
        result = celery.AsyncResult(task_id)
        return {
            'id': task_id,
            'status': result.status,
            'result': result.result,
            'traceback': result.traceback,
        }
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        return None


# Production Recommendations
"""
PRODUCTION DEPLOYMENT CHECKLIST:

1. Install Redis:
   - Ensure Redis is running in production
   - Configure Redis persistence (RDB or AOF)
   - Set up Redis authentication
   - Monitor Redis memory usage

2. Celery Workers:
   - Run multiple workers: celery -A celery_app worker -n worker1@%h
   - Use Supervisor or Systemd for auto-restart
   - Monitor worker health

3. Celery Beat Scheduler:
   - Run separate beat process: celery -A celery_app beat
   - Use persistent schedule storage

4. Monitoring:
   - Setup Flower for monitoring: celery -A celery_app flower
   - Configure error tracking (Sentry)
   - Monitor task success/failure rates

5. Performance:
   - Tune worker concurrency
   - Set appropriate task timeouts
   - Monitor task queue depth

6. Security:
   - Use authentication for Redis
   - Validate task inputs
   - Don't pass sensitive data in tasks

7. Logging:
   - Configure centralized logging
   - Monitor error rates
   - Set up alerts for failures
"""
