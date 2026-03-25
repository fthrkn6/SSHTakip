"""
Redis Cache Integration & Verification
Ensures Redis caching works across application for performance optimization
"""

from functools import wraps
from datetime import timedelta
import hashlib
import json
from flask import request, current_app
from utils_performance import cache_manager

# Cache decorator for database queries
def cache_query(ttl=None, key_prefix=None):
    """
    Decorator to cache database query results
    
    Usage:
        @cache_query(ttl=timedelta(hours=1), key_prefix='equipment')
        def get_active_equipment(project_code):
            return Equipment.query.filter_by(project_code=project_code).all()
    """
    if ttl is None:
        ttl = timedelta(hours=1)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix or func.__name__}:{func.__name__}"
            
            # Add arguments to key
            key_args = str(args) + str(sorted(kwargs.items()))
            cache_key += f":{hashlib.md5(key_args.encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                current_app.logger.debug(f'Cache HIT: {cache_key}')
                return cached_result
            
            # Execute function if not cached
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_key, result, ttl=ttl)
            current_app.logger.debug(f'Cache MISS: {cache_key} (stored for {ttl})')
            
            return result
        return wrapper
    return decorator


# Cache decorator for API endpoints
def cache_endpoint(ttl=None, vary_by=None):
    """
    Decorator to cache API endpoint responses
    
    Usage:
        @cache_endpoint(ttl=timedelta(minutes=5), vary_by=['user_id', 'project_code'])
        def api_get_kpis():
            return jsonify(...)
    """
    if ttl is None:
        ttl = timedelta(minutes=5)
    if vary_by is None:
        vary_by = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from request and vary_by params
            cache_key = f"endpoint:{func.__name__}"
            
            # Add URL parameters
            if request.args:
                cache_key += f":{request.args}"
            
            # Add vary_by parameters (from request or session)
            for param in vary_by:
                if param in request.args:
                    cache_key += f":{param}={request.args.get(param)}"
            
            # Hash the key to keep it reasonable length
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
            # Try cache
            cached_response = cache_manager.get(cache_key)
            if cached_response is not None:
                current_app.logger.debug(f'Endpoint cache HIT: {func.__name__}')
                return cached_response
            
            # Execute endpoint
            response = func(*args, **kwargs)
            
            # Cache the response
            cache_manager.set(cache_key, response, ttl=ttl)
            current_app.logger.debug(f'Endpoint cache MISS: {func.__name__}')
            
            return response
        return wrapper
    return decorator


# Verify Redis connectivity
def verify_redis_connection():
    """
    Verify Redis is properly connected
    Returns: (is_connected: bool, stats: dict)
    """
    try:
        # Test set/get
        test_key = 'redis_health_check'
        cache_manager.set(test_key, 'ok', ttl=timedelta(seconds=5))
        result = cache_manager.get(test_key)
        cache_manager.delete(test_key)
        
        if result == 'ok':
            return True, {
                'status': 'healthy',
                'backend': 'redis',
                'test': 'passed'
            }
    except Exception as e:
        current_app.logger.warning(f'Redis health check failed: {str(e)}')
        return False, {
            'status': 'degraded',
            'backend': 'local',
            'error': str(e),
            'fallback': 'using local cache'
        }


# Cache invalidation utilities
def invalidate_cache_pattern(pattern):
    """
    Invalidate all cache keys matching a pattern
    
    Usage:
        invalidate_cache_pattern('equipment:*')  # Clear all equipment caches
    """
    count = cache_manager.clear_pattern(pattern)
    current_app.logger.info(f'Invalidated {count} cache keys matching: {pattern}')
    return count


def invalidate_on_model_change(model_name):
    """
    Decorator to invalidate related cache entries when model is modified
    
    Usage:
        @invalidate_on_model_change('equipment')
        def update_equipment(equipment_id, data):
            # ... update logic
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the function
            result = func(*args, **kwargs)
            
            # Invalidate related caches
            patterns = [
                f'{model_name}:*',
                'dashboard:*',
                'metrics:*',
                f'{model_name}_list:*'
            ]
            
            for pattern in patterns:
                cache_manager.clear_pattern(pattern)
            
            current_app.logger.info(f'Cache cleared for model: {model_name}')
            return result
        return wrapper
    return decorator


# Cache warming (pre-load frequently accessed data)
def warm_cache():
    """
    Pre-load commonly accessed data into cache
    Useful during startup or low-usage periods
    """
    from models import Equipment, Failure, MaintenancePlan
    
    try:
        # Cache all active equipment
        equipment_data = Equipment.query.filter_by(is_active=True).all()
        cache_manager.set('equipment:active:all', 
                         [e.to_dict() for e in equipment_data],
                         ttl=timedelta(hours=2))
        
        # Cache recent failures
        failures = Failure.query.order_by(Failure.created_date.desc()).limit(100).all()
        cache_manager.set('failures:recent:100',
                         [f.to_dict() for f in failures],
                         ttl=timedelta(hours=1))
        
        # Cache active maintenance plans
        maintenance = MaintenancePlan.query.filter_by(status='active').all()
        cache_manager.set('maintenance:active:all',
                         [m.to_dict() for m in maintenance],
                         ttl=timedelta(hours=1))
        
        current_app.logger.info('Cache warming completed successfully')
        return True
    except Exception as e:
        current_app.logger.error(f'Cache warming failed: {str(e)}')
        return False


# Cache statistics dashboard
def get_cache_stats():
    """
    Get detailed cache statistics
    Returns: dict with cache performance metrics
    """
    stats = cache_manager.get_stats()
    
    if not stats:
        return {
            'status': 'no_stats',
            'message': 'Cache statistics not available'
        }
    
    return {
        'cache_type': stats.get('type', 'unknown'),
        'cache_size': stats.get('size', 0),
        'available_memory': stats.get('available_memory', 'N/A'),
        'connected_clients': stats.get('connected_clients', 0),
        'used_memory': stats.get('used_memory', 'N/A'),
        'total_commands': stats.get('total_commands', 0),
        'hits': stats.get('hits', 0),
        'misses': stats.get('misses', 0),
        'hit_rate': stats.get('hit_rate', 0),
        'evictions': stats.get('evictions', 0)
    }


# Configuration validation
def validate_cache_config():
    """
    Validate Redis/Cache configuration
    Returns: (is_valid: bool, issues: list)
    """
    issues = []
    
    # Check environment variables
    if not current_app.config.get('REDIS_URL'):
        issues.append('REDIS_URL not configured')
    
    if not current_app.config.get('CACHE_DEFAULT_TIMEOUT'):
        issues.append('CACHE_DEFAULT_TIMEOUT not set')
    
    # Check connection
    is_connected, stats = verify_redis_connection()
    if not is_connected:
        issues.append(f'Redis connection failed: {stats.get("error", "unknown")}')
    
    return len(issues) == 0, issues


# Usage example
if __name__ == '__main__':
    print("Redis Cache Integration Utilities Loaded")
    print("Available functions:")
    print("  - cache_query()")
    print("  - cache_endpoint()")
    print("  - verify_redis_connection()")
    print("  - invalidate_cache_pattern()")
    print("  - invalidate_on_model_change()")
    print("  - warm_cache()")
    print("  - get_cache_stats()")
    print("  - validate_cache_config()")
