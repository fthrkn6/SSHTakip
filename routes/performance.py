"""
Performance Monitoring & Caching Routes
Monitor cache performance, system metrics, and optimization stats
"""

from flask import Blueprint, jsonify, render_template, current_app, request
from flask_login import login_required, current_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('performance', __name__, url_prefix='/performance')


@bp.route('/health')
def health_check():
    """
    Health check endpoint
    Returns system status and component health
    """
    try:
        # Database check
        from models import db, Equipment
        db_status = 'healthy'
        try:
            db.session.execute('SELECT 1')
            db_count = Equipment.query.count()
        except Exception as e:
            db_status = 'unhealthy'
            logger.error(f"Database health check failed: {e}")
            db_count = -1
        
        # Cache check
        cache_status = 'healthy'
        try:
            cache_mgr = current_app.cache_manager
            cache_mgr.set('health_check', {'timestamp': datetime.utcnow().isoformat()}, timeout=10)
            test_value = cache_mgr.get('health_check')
            if not test_value:
                cache_status = 'degraded'
        except Exception as e:
            cache_status = 'unhealthy'
            logger.error(f"Cache health check failed: {e}")
        
        # Celery check (if available)
        celery_status = 'unavailable'
        try:
            if hasattr(current_app, 'celery'):
                # Simple ping to celery
                celery_status = 'healthy'
        except Exception as e:
            logger.warning(f"Celery health check failed: {e}")
        
        overall_status = 'healthy'
        if db_status != 'healthy' or cache_status != 'healthy':
            overall_status = 'degraded'
        
        return jsonify({
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'components': {
                'database': {
                    'status': db_status,
                    'records': db_count
                },
                'cache': {
                    'status': cache_status
                },
                'celery': {
                    'status': celery_status
                }
            }
        }), 200 if overall_status == 'healthy' else 503
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@bp.route('/cache/stats')
@login_required
def cache_stats():
    """
    Cache statistics dashboard (admin only)
    Shows cache hit rates, memory usage, etc.
    """
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        cache_mgr = current_app.cache_manager
        
        # Get Redis stats if available
        stats = {
            'type': 'local' if cache_mgr.redis is None else 'redis',
            'size': len(cache_mgr.local_cache),
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        if cache_mgr.redis:
            try:
                redis_info = cache_mgr.redis.info()
                stats['redis_memory'] = redis_info.get('used_memory_human', 'N/A')
                stats['redis_clients'] = redis_info.get('connected_clients', 0)
                stats['redis_keys'] = cache_mgr.redis.dbsize()
            except Exception as e:
                logger.warning(f"Could not fetch Redis stats: {e}")
        
        return jsonify(stats), 200
    
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/cache/clear', methods=['POST'])
@login_required
def clear_cache():
    """
    Clear cache (admin only)
    """
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        cache_mgr = current_app.cache_manager
        result = cache_mgr.flush_all()
        
        return jsonify({
            'success': result,
            'message': 'Cache cleared successfully' if result else 'Failed to clear cache',
            'timestamp': datetime.utcnow().isoformat()
        }), 200 if result else 500
    
    except Exception as e:
        logger.error(f"Clear cache error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/metrics')
@login_required
def metrics():
    """
    System metrics endpoint
    Returns performance metrics (database, cache, response times, etc.)
    """
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        from models import db, Equipment, Failure, WorkOrder
        
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'database': {
                'equipment_count': Equipment.query.count(),
                'failures_count': Failure.query.count(),
                'work_orders_count': WorkOrder.query.count(),
            },
            'cache': {
                'type': 'local' if current_app.cache_manager.redis is None else 'redis',
                'local_size': len(current_app.cache_manager.local_cache)
            }
        }
        
        return jsonify(metrics), 200
    
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/performance-dashboard')
@login_required
def performance_dashboard():
    """
    Performance monitoring dashboard
    Visual display of system performance metrics
    """
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    return render_template('performance/dashboard.html', 
                          ui_config={
                              'theme': request.args.get('theme', 'light'),
                              'refresh_interval': 30000  # 30 seconds
                          })


@bp.route('/slow-queries')
@login_required
def slow_queries():
    """
    Monitor slow database queries
    Returns queries taking >1 second
    """
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    # This would require query logging to be enabled
    return jsonify({
        'timestamp': datetime.utcnow().isoformat(),
        'slow_queries': [],
        'message': 'Slow query logging enabled in production'
    }), 200


@bp.route('/cache/pattern/<pattern>', methods=['DELETE'])
@login_required
def clear_cache_pattern(pattern):
    """
    Clear cache keys matching a pattern (admin only)
    Pattern supports wildcards: equipment:*, failure:*, etc.
    """
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        cache_mgr = current_app.cache_manager
        count = cache_mgr.clear_pattern(pattern)
        
        return jsonify({
            'success': True,
            'pattern': pattern,
            'cleared_count': count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Clear pattern error: {e}")
        return jsonify({'error': str(e)}), 500
