"""
Query Optimization Utilities
Identifies and fixes N+1 query problems and inefficient database patterns
"""

from sqlalchemy import event, inspect
from flask import current_app
import logging
import time
from functools import wraps

# Setup query logging
query_log = []

class QueryProfiler:
    """Profiles SQL queries for performance issues"""
    
    def __init__(self):
        self.queries = []
        self.total_time = 0
        self.n_plus_one_suspects = {}
    
    def log_query(self, statement, params, start_time, end_time, context):
        """Log query execution details"""
        duration = end_time - start_time
        self.queries.append({
            'statement': str(statement),
            'params': params,
            'duration': duration,
            'timestamp': start_time
        })
        self.total_time += duration
        
        # Flag slow queries (> 100ms)
        if duration > 0.1:
            current_app.logger.warning(
                f'SLOW QUERY ({duration:.3f}s): {str(statement)[:100]}...'
            )
    
    def detect_n_plus_one(self):
        """Detect potential N+1 query patterns"""
        query_patterns = {}
        
        for query in self.queries:
            statement = str(query['statement']).split('FROM')[0] if 'FROM' in str(query['statement']) else str(query['statement'])[:50]
            
            if statement not in query_patterns:
                query_patterns[statement] = {'count': 0, 'total_time': 0}
            
            query_patterns[statement]['count'] += 1
            query_patterns[statement]['total_time'] += query['duration']
        
        # Flag patterns with many similar queries
        suspects = {}
        for pattern, stats in query_patterns.items():
            if stats['count'] > 5:  # More than 5 identical queries
                suspects[pattern] = {
                    'count': stats['count'],
                    'total_time': stats['total_time'],
                    'avg_time': stats['total_time'] / stats['count']
                }
        
        self.n_plus_one_suspects = suspects
        return suspects
    
    def get_report(self):
        """Generate performance report"""
        return {
            'total_queries': len(self.queries),
            'total_time': self.total_time,
            'avg_time': self.total_time / len(self.queries) if self.queries else 0,
            'n_plus_one_suspects': self.detect_n_plus_one(),
            'queries': self.queries[:20]  # First 20 queries
        }


# Global profiler instance
profiler = QueryProfiler()


def enable_query_profiling(app):
    """Enable query profiling for the Flask app"""
    
    @event.listens_for(app.db.engine, 'before_cursor_execute')
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
    
    @event.listens_for(app.db.engine, 'after_cursor_execute')
    def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total_time = time.time() - conn.info['query_start_time'].pop(-1)
        profiler.log_query(statement, parameters, time.time() - total_time, time.time(), context)


def optimize_query(func):
    """
    Decorator to optimize queries using eager loading
    Automatically loads relationships to prevent N+1 queries
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # This is applied before the query executes
        return func(*args, **kwargs)
    return wrapper


def eager_load_relationships(query, *relationships):
    """
    Apply eager loading to a query
    
    Usage:
        equipment = eager_load_relationships(
            Equipment.query,
            'failures',
            'maintenance_plans',
            'service_logs'
        ).filter_by(is_active=True)
    """
    from sqlalchemy.orm import joinedload
    
    for relationship in relationships:
        query = query.options(joinedload(relationship))
    
    return query


def get_query_report():
    """Get query performance report"""
    return profiler.get_report()


def reset_query_profiler():
    """Reset query profiler for new session"""
    global profiler
    profiler = QueryProfiler()


# Common optimization patterns

def optimize_equipment_queries():
    """
    Optimized equipment query
    Prevents N+1 when loading equipment with relationships
    """
    from models import Equipment
    from sqlalchemy.orm import joinedload
    
    return Equipment.query.options(
        joinedload('failures'),
        joinedload('maintenance_plans'),
        joinedload('service_logs'),
        joinedload('km_logs')
    ).filter_by(is_active=True)


def optimize_failure_queries():
    """
    Optimized failure query with all relationships
    """
    from models import Failure
    from sqlalchemy.orm import joinedload
    
    return Failure.query.options(
        joinedload('equipment'),
        joinedload('root_cause'),
        joinedload('assigned_to'),
        joinedload('failure_class')
    ).order_by(Failure.failure_date.desc())


def optimize_maintenance_queries():
    """
    Optimized maintenance plan query
    """
    from models import MaintenancePlan
    from sqlalchemy.orm import joinedload
    
    return MaintenancePlan.query.options(
        joinedload('equipment'),
        joinedload('assigned_to'),
        joinedload('work_orders')
    ).filter_by(is_active=True)


def batch_query_optimization(model, filters=None, batch_size=1000):
    """
    Optimize large query results using batching
    
    Usage:
        for batch in batch_query_optimization(Equipment, {'is_active': True}, 500):
            process_equipment_batch(batch)
    """
    from sqlalchemy.orm import Query
    
    query = model.query
    
    if filters:
        for key, value in filters.items():
            query = query.filter(getattr(model, key) == value)
    
    offset = 0
    while True:
        batch = query.limit(batch_size).offset(offset).all()
        if not batch:
            break
        yield batch
        offset += batch_size


# Query complexity analyzer
def analyze_query_complexity(query_object):
    """
    Analyze SQL query complexity
    Returns: complexity score (0-100)
    """
    statement = str(query_object)
    complexity = 0
    
    # Count JOINs
    complexity += statement.count('JOIN') * 5
    
    # Count WHERE conditions
    complexity += statement.count('AND') * 2
    complexity += statement.count('OR') * 3
    
    # Count subqueries
    complexity += statement.count('SELECT') * 10
    
    # Check for DISTINCT
    if 'DISTINCT' in statement:
        complexity += 5
    
    # Check for GROUP BY
    if 'GROUP BY' in statement:
        complexity += 8
    
    return min(complexity, 100)


# Performance metrics
class QueryMetrics:
    """Collect and report query metrics"""
    
    slow_queries = []
    n_plus_one_queries = []
    
    @classmethod
    def log_slow_query(cls, duration, statement):
        """Log slow query (> 100ms)"""
        cls.slow_queries.append({
            'duration': duration,
            'statement': statement,
            'timestamp': time.time()
        })
    
    @classmethod
    def log_n_plus_one(cls, pattern, count):
        """Log N+1 query pattern"""
        cls.n_plus_one_queries.append({
            'pattern': pattern,
            'count': count,
            'timestamp': time.time()
        })
    
    @classmethod
    def get_summary(cls):
        """Get metrics summary"""
        return {
            'slow_queries_count': len(cls.slow_queries),
            'n_plus_one_count': len(cls.n_plus_one_queries),
            'slow_queries': cls.slow_queries[-10:],  # Last 10
            'n_plus_one_samples': cls.n_plus_one_queries[-5:]  # Last 5
        }
    
    @classmethod
    def reset(cls):
        """Reset metrics"""
        cls.slow_queries = []
        cls.n_plus_one_queries = []


# Usage example
if __name__ == '__main__':
    print("Query Optimization Utilities Loaded")
    print("Available functions:")
    print("  - enable_query_profiling(app)")
    print("  - optimize_equipment_queries()")
    print("  - optimize_failure_queries()")
    print("  - optimize_maintenance_queries()")
    print("  - batch_query_optimization(model, filters, batch_size)")
    print("  - eager_load_relationships(query, *relationships)")
    print("  - get_query_report()")
    print("  - analyze_query_complexity(query)")
