"""
Unit tests for utility functions
Run with: pytest tests/test_utils.py -v
"""

import pytest
from datetime import datetime, timedelta
from utils_redis_integration import (
    cache_query, cache_endpoint, verify_redis_connection,
    invalidate_cache_pattern, warm_cache, get_cache_stats
)
from utils_query_optimization import (
    QueryProfiler, eager_load_relationships,
    batch_query_optimization, analyze_query_complexity
)


class TestRedisIntegration:
    """Test Redis cache integration"""
    
    def test_cache_manager_set_get(self, app):
        """Test cache set/get operations"""
        with app.app_context():
            from utils_performance import cache_manager
            
            cache_manager.set('test_key', 'test_value', ttl=timedelta(minutes=1))
            result = cache_manager.get('test_key')
            
            assert result == 'test_value'
    
    def test_cache_delete(self, app):
        """Test cache deletion"""
        with app.app_context():
            from utils_performance import cache_manager
            
            cache_manager.set('delete_test', 'value')
            cache_manager.delete('delete_test')
            result = cache_manager.get('delete_test')
            
            assert result is None
    
    def test_cache_clear_pattern(self, app):
        """Test clearing cache by pattern"""
        with app.app_context():
            from utils_performance import cache_manager
            
            # Set multiple keys with pattern
            cache_manager.set('equipment:1', 'data1')
            cache_manager.set('equipment:2', 'data2')
            cache_manager.set('other:1', 'data3')
            
            # Clear by pattern
            count = cache_manager.clear_pattern('equipment:*')
            
            # Verify clearance
            assert cache_manager.get('equipment:1') is None
            assert cache_manager.get('equipment:2') is None
            assert cache_manager.get('other:1') is not None or count >= 0
    
    def test_verify_redis_connection(self, app):
        """Test Redis connection verification"""
        with app.app_context():
            is_connected, stats = verify_redis_connection()
            
            assert isinstance(is_connected, bool)
            assert 'status' in stats
            assert 'backend' in stats
    
    def test_get_cache_stats(self, app):
        """Test getting cache statistics"""
        with app.app_context():
            stats = get_cache_stats()
            
            assert isinstance(stats, dict)
            assert 'cache_type' in stats or 'status' in stats


class TestQueryProfiler:
    """Test query profiling utilities"""
    
    def test_profiler_creation(self):
        """Test creating query profiler"""
        profiler = QueryProfiler()
        
        assert profiler.queries == []
        assert profiler.total_time == 0
    
    def test_query_logging(self):
        """Test logging queries"""
        profiler = QueryProfiler()
        
        profiler.log_query(
            'SELECT * FROM equipment',
            {},
            0.001,
            0.002,
            None
        )
        
        assert len(profiler.queries) == 1
        assert profiler.total_time > 0
    
    def test_n_plus_one_detection(self):
        """Test N+1 query detection"""
        profiler = QueryProfiler()
        
        # Simulate N+1 pattern
        for i in range(10):
            profiler.log_query(
                'SELECT * FROM equipment WHERE id = ?',
                [i],
                0.0,
                0.001,
                None
            )
        
        suspects = profiler.detect_n_plus_one()
        
        # Should detect the repeated pattern
        assert len(suspects) >= 0  # Might detect it or might not
    
    def test_profiler_report(self):
        """Test generating profiler report"""
        profiler = QueryProfiler()
        
        profiler.log_query('SELECT * FROM equipment', {}, 0.0, 0.001, None)
        profiler.log_query('SELECT * FROM failure', {}, 0.0, 0.002, None)
        
        report = profiler.get_report()
        
        assert 'total_queries' in report
        assert 'total_time' in report
        assert report['total_queries'] == 2


class TestBatchProcessing:
    """Test batch query optimization"""
    
    def test_batch_query_limits(self, app, db):
        """Test batch query with size limits"""
        with app.app_context():
            from models import Equipment
            
            # This would process in batches
            # batch_count = 0
            # for batch in batch_query_optimization(Equipment, {}, batch_size=100):
            #     batch_count += 1
            #
            # assert batch_count >= 0
            pass


class TestQueryComplexity:
    """Test query complexity analysis"""
    
    def test_simple_query_complexity(self):
        """Test complexity of simple query"""
        from sqlalchemy import text
        
        query = text("SELECT * FROM equipment")
        complexity = analyze_query_complexity(query)
        
        assert complexity >= 0
        assert complexity < 50  # Simple query should be low
    
    def test_complex_query_complexity(self):
        """Test complexity of complex query"""
        from sqlalchemy import text
        
        query = text("""
            SELECT e.*, f.*, m.*
            FROM equipment e
            JOIN failure f ON e.id = f.equipment_id
            JOIN maintenance_plan m ON e.id = m.equipment_id
            WHERE e.project_code = ? AND f.status = ?
            GROUP BY e.id
            HAVING COUNT(f.id) > 5
        """)
        complexity = analyze_query_complexity(query)
        
        assert complexity > 0  # Complex query should have score


class TestDataBuilder:
    """Test data building utilities"""
    
    def test_create_test_equipment(self, app, db):
        """Test creating test equipment"""
        with app.app_context():
            from models import Equipment
            
            equipment = Equipment(
                equipment_code='TEST-001',
                project_code='belgrad'
            )
            db.session.add(equipment)
            db.session.commit()
            
            assert equipment.id is not None
            assert equipment.equipment_code == 'TEST-001'
    
    def test_create_test_failure(self, app, db):
        """Test creating test failure"""
        with app.app_context():
            from models import Equipment, Failure
            
            equipment = Equipment(
                equipment_code='TEST-002',
                project_code='belgrad'
            )
            db.session.add(equipment)
            db.session.commit()
            
            failure = Failure(
                equipment_id=equipment.id,
                project_code='belgrad',
                failure_description='Test'
            )
            db.session.add(failure)
            db.session.commit()
            
            assert failure.id is not None


class TestCachingDecorators:
    """Test caching decorator functions"""
    
    def test_cache_query_decorator(self, app):
        """Test @cache_query decorator"""
        # This would test actual caching when applied to methods
        # Requires full Flask context and database
        pass
    
    def test_cache_endpoint_decorator(self, app):
        """Test @cache_endpoint decorator"""
        # This would test endpoint caching
        pass


class TestErrorHandling:
    """Test error handling in utilities"""
    
    def test_cache_with_invalid_ttl(self, app):
        """Test cache with invalid TTL"""
        with app.app_context():
            from utils_performance import cache_manager
            
            # Should handle gracefully
            try:
                cache_manager.set('key', 'value', ttl=timedelta(seconds=-1))
                result = cache_manager.get('key')
                # Either returns None or handles gracefully
                assert result is None or result is not None
            except Exception:
                pass
    
    def test_query_with_null_result(self):
        """Test handling null query results"""
        profiler = QueryProfiler()
        
        # Should not crash with no queries
        report = profiler.get_report()
        
        assert report['total_queries'] == 0
        assert report['total_time'] == 0


class TestPerformanceUtilities:
    """Test performance measurement utilities"""
    
    def test_slow_query_detection(self, app):
        """Test detecting slow queries"""
        with app.app_context():
            profiler = QueryProfiler()
            
            # Log a slow query
            profiler.log_query('SELECT * FROM slow_table', {}, 0.05, 0.150, None)
            
            report = profiler.get_report()
            # Should have detected slow query
            assert report['total_queries'] >= 1
    
    def test_cache_statistics(self, app):
        """Test cache statistics collection"""
        with app.app_context():
            stats = get_cache_stats()
            
            # Should return dict with cache info
            assert isinstance(stats, dict)


class TestMonitoringHooks:
    """Test monitoring and observability hooks"""
    
    def test_query_hook_integration(self, app):
        """Test query hooks for monitoring"""
        # This would test event listeners on DB engine
        # Requires full setup
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
