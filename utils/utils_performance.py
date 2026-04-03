"""
Performance & Caching Layer
Redis integration, Query optimization, Async task support
"""

from typing import Any, Callable, Optional, Dict, List
from functools import wraps
from datetime import timedelta
import logging
import json

logger = logging.getLogger(__name__)


class CacheConfig:
    """Cache configuration"""
    
    # Default TTLs
    TTL_SHORT = timedelta(minutes=5)      # 5 minutes
    TTL_MEDIUM = timedelta(hours=1)       # 1 hour
    TTL_LONG = timedelta(hours=24)        # 24 hours
    TTL_WEEK = timedelta(days=7)          # 7 days
    
    # Cache prefixes
    PREFIX_EQUIPMENT = 'eq:'
    PREFIX_FAILURE = 'failure:'
    PREFIX_KPI = 'kpi:'
    PREFIX_USER = 'user:'
    PREFIX_PROJECT = 'proj:'
    PREFIX_REPORT = 'report:'


class CacheManager:
    """Manage caching layer"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.local_cache: Dict[str, Any] = {}
    
    def get(self, key: str, default=None) -> Optional[Any]:
        """Get from cache"""
        if self.redis:
            try:
                value = self.redis.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
        
        return self.local_cache.get(key, default)
    
    def set(self, key: str, value: Any, ttl: timedelta = CacheConfig.TTL_MEDIUM) -> bool:
        """Set cache value"""
        try:
            if self.redis:
                self.redis.setex(
                    key,
                    int(ttl.total_seconds()),
                    json.dumps(value)
                )
            else:
                self.local_cache[key] = value
            return True
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cache key"""
        try:
            if self.redis:
                self.redis.delete(key)
            if key in self.local_cache:
                del self.local_cache[key]
            return True
        except Exception as e:
            logger.error(f"Cache delete failed: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern"""
        count = 0
        if self.redis:
            try:
                keys = self.redis.keys(pattern)
                if keys:
                    count = self.redis.delete(*keys)
            except Exception as e:
                logger.error(f"Clear pattern failed: {e}")
        
        # Clear local cache
        to_delete = [k for k in self.local_cache.keys() if pattern.replace('*', '') in k]
        for k in to_delete:
            del self.local_cache[k]
            count += 1
        
        return count
    
    def flush_all(self) -> bool:
        """Clear all caches"""
        try:
            if self.redis:
                self.redis.flushdb()
            self.local_cache.clear()
            logger.info("Cache flushed")
            return True
        except Exception as e:
            logger.error(f"Flush failed: {e}")
            return False


# Caching Decorators
def cache_result(key_prefix: str, ttl: timedelta = CacheConfig.TTL_MEDIUM):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            cache_key = f"{key_prefix}:{':'.join(str(a) for a in args)}"
            if kwargs:
                cache_key += f":{json.dumps(kwargs, sort_keys=True)}"
            
            # Try getting from cache
            from app import cache_manager
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cache miss: {cache_key}")
            
            return result
        
        return wrapper
    
    return decorator


def invalidate_cache(pattern: str):
    """Decorator to invalidate cache after function execution"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            from app import cache_manager
            cache_manager.clear_pattern(pattern)
            logger.info(f"Cache invalidated: {pattern}")
            
            return result
        
        return wrapper
    
    return decorator


# Query Optimization Helpers
class QueryOptimizer:
    """Optimize database queries"""
    
    @staticmethod
    def add_eager_loading(query, *relations):
        """Add eager loading to query"""
        for relation in relations:
            query = query.options(
                load(relation)
            )
        return query
    
    @staticmethod
    def optimize_equipment_query(query):
        """Optimize equipment queries with common relations"""
        from sqlalchemy.orm import joinedload
        return query.options(
            joinedload('*')  # Load all relationships
        )
    
    @staticmethod
    def optimize_failure_query(query):
        """Optimize failure queries"""
        from sqlalchemy.orm import joinedload
        return query.options(
            joinedload('equipment'),
            joinedload('rca_analysis')
        )
    
    @staticmethod
    def optimize_user_query(query):
        """Optimize user queries"""
        from sqlalchemy.orm import joinedload
        return query.options(
            joinedload('roles'),
            joinedload('projects')
        )


# Async Task Configuration (Celery-ready)
class AsyncTaskConfig:
    """Async task configuration"""
    
    # Task Queues
    QUEUE_HIGH = 'high_priority'
    QUEUE_DEFAULT = 'default'
    QUEUE_LOW = 'low_priority'
    
    # Task Names
    TASK_GENERATE_REPORT = 'tasks.generate_report'
    TASK_EXPORT_DATA = 'tasks.export_data'
    TASK_SEND_EMAIL = 'tasks.send_email'
    TASK_SYNC_KM = 'tasks.sync_km_data'
    TASK_ANALYZE_FAILURE = 'tasks.analyze_failure'
    TASK_CALCULATE_KPI = 'tasks.calculate_kpi'


# Initialize global cache manager
cache_manager: Optional[CacheManager] = None


def init_cache(redis_client=None):
    """Initialize cache manager"""
    global cache_manager
    cache_manager = CacheManager(redis_client)
    logger.info("Cache manager initialized")
    return cache_manager
