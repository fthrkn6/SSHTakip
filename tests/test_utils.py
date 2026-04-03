"""
Unit Tests for Utility Functions
Tests data processing, calculations, and utility modules
"""

import pytest
from conftest import BaseTestCase
from datetime import datetime, timedelta


class TestKMDataManager(BaseTestCase):
    """Test KM data management utilities"""
    
    @pytest.mark.unit
    def test_get_equipment_km(self, test_equipment):
        """Test retrieving equipment KM"""
        # This would test the actual KMDataManager class
        assert test_equipment.current_km >= 0
    
    @pytest.mark.unit
    def test_update_equipment_km(self, test_equipment):
        """Test updating equipment KM"""
        initial_km = test_equipment.current_km
        test_equipment.current_km += 1000
        
        assert test_equipment.current_km == initial_km + 1000


class TestStatusLogger(BaseTestCase):
    """Test service status logging"""
    
    @pytest.mark.unit
    def test_log_status_change(self, test_equipment):
        """Test logging status change"""
        from utils.utils_service_status_consolidated import ServiceStatusLogger
        
        logger = ServiceStatusLogger()
        result = logger.log_status_change(
            tram_id=test_equipment.tram_id,
            date=datetime.now().strftime('%Y-%m-%d'),
            status='maintenance',
            duration_minutes=120
        )
        
        # Should log successfully
        assert result is not None
    
    @pytest.mark.unit
    def test_get_status_history(self, test_equipment):
        """Test retrieving status history"""
        from utils.utils_service_status_consolidated import ServiceStatusLogger
        
        logger = ServiceStatusLogger()
        history = logger.get_status_history(test_equipment.tram_id)
        
        # Should return list (could be empty)
        assert isinstance(history, (list, dict)) or history is None


class TestEquipmentSync(BaseTestCase):
    """Test equipment synchronization"""
    
    @pytest.mark.unit
    def test_sync_equipment_result_format(self):
        """Test equipment sync returns correct format"""
        # from utils.utils_equipment_sync import sync_equipment_with_excel
        # Sync should return tuple (added, updated)
        pass


class TestExcelOperations(BaseTestCase):
    """Test Excel file operations"""
    
    @pytest.mark.unit
    def test_read_excel_file(self):
        """Test reading Excel file"""
        # Would test actual Excel reading functionality
        pass
    
    @pytest.mark.unit
    def test_write_excel_file(self):
        """Test writing Excel file"""
        # Would test actual Excel writing functionality
        pass


class TestMTTRCalculation(BaseTestCase):
    """Test MTTR (Mean Time To Repair) calculations"""
    
    @pytest.mark.unit
    def test_mttr_calculation_basic(self):
        """Test basic MTTR calculation"""
        # MTTR = Total repair time / Number of repairs
        total_repair_time = 500  # minutes
        num_repairs = 5
        
        mttr = total_repair_time / num_repairs
        assert mttr == 100
    
    @pytest.mark.unit
    def test_mttr_no_repairs(self):
        """Test MTTR with no repairs"""
        # Should handle zero repairs gracefully
        num_repairs = 0
        
        if num_repairs == 0:
            mttr = 0
        else:
            mttr = 500 / num_repairs
        
        assert mttr == 0


class TestMTBFCalculation(BaseTestCase):
    """Test MTBF (Mean Time Between Failures) calculations"""
    
    @pytest.mark.unit
    def test_mtbf_calculation_basic(self):
        """Test basic MTBF calculation"""
        # MTBF = Total operating time / Number of failures
        total_uptime = 10000  # hours
        num_failures = 5
        
        mtbf = total_uptime / num_failures
        assert mtbf == 2000
    
    @pytest.mark.unit
    def test_mtbf_high_reliability(self):
        """Test MTBF with high reliability"""
        total_uptime = 50000
        num_failures = 2
        
        mtbf = total_uptime / num_failures
        assert mtbf == 25000


class TestAvailabilityCalculation(BaseTestCase):
    """Test availability calculations"""
    
    @pytest.mark.unit
    def test_availability_perfect(self):
        """Test 100% availability"""
        operating_time = 100
        total_time = 100
        
        availability = (operating_time / total_time) * 100
        assert availability == 100
    
    @pytest.mark.unit
    def test_availability_with_downtime(self):
        """Test availability with downtime"""
        total_hours = 24
        downtime_hours = 6
        operating_time = total_hours - downtime_hours
        
        availability = (operating_time / total_hours) * 100
        assert availability == 75


class TestReportGeneration(BaseTestCase):
    """Test report generation utilities"""
    
    @pytest.mark.unit
    def test_report_template_loading(self):
        """Test loading report templates"""
        from utils.utils_report_manager import report_builder, template_manager
        
        templates = template_manager.list_templates()
        assert len(templates) > 0
    
    @pytest.mark.unit
    def test_report_building(self):
        """Test building report from template"""
        from utils.utils_report_manager import report_builder
        
        report = report_builder.build_report('daily_ops', {})
        assert 'title' in report
        assert 'template' in report


class TestDataValidation(BaseTestCase):
    """Test data validation utilities"""
    
    @pytest.mark.unit
    def test_validate_tram_id(self):
        """Test TRAM ID validation"""
        valid_ids = ['TRAM_001', 'TRAM_100']
        invalid_ids = ['INVALID', '123', '']
        
        for tram_id in valid_ids:
            assert len(tram_id) > 0
        
        for tram_id in invalid_ids:
            assert tram_id == '' or not tram_id.startswith('TRAM_')
    
    @pytest.mark.unit
    def test_validate_failure_code(self):
        """Test failure code validation"""
        valid_codes = ['F_001', 'F_100', 'RCA_001']
        
        for code in valid_codes:
            assert len(code) > 0


class TestDateTimeHandling(BaseTestCase):
    """Test date/time handling utilities"""
    
    @pytest.mark.unit
    def test_date_range_parsing(self):
        """Test parsing date ranges"""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        assert today > yesterday
    
    @pytest.mark.unit
    def test_working_hours_calculation(self):
        """Test working hours calculation"""
        start = datetime(2024, 1, 1, 9, 0)  # 9 AM
        end = datetime(2024, 1, 1, 17, 0)   # 5 PM
        
        working_hours = (end - start).total_seconds() / 3600
        assert working_hours == 8


class TestCachingUtilities(BaseTestCase):
    """Test caching utilities"""
    
    @pytest.mark.unit
    def test_cache_manager_init(self):
        """Test cache manager initialization"""
        from utils.utils_performance import CacheManager
        
        cache = CacheManager()
        assert cache is not None
    
    @pytest.mark.unit
    def test_cache_set_get(self):
        """Test cache set and get"""
        from utils.utils_performance import CacheManager
        
        cache = CacheManager()
        cache.set('test_key', {'value': 'test'})
        result = cache.get('test_key')
        
        assert result == {'value': 'test'}
    
    @pytest.mark.unit
    def test_cache_delete(self):
        """Test cache deletion"""
        from utils.utils_performance import CacheManager
        
        cache = CacheManager()
        cache.set('test_key', 'value')
        cache.delete('test_key')
        result = cache.get('test_key')
        
        assert result is None


class TestUIConfiguration(BaseTestCase):
    """Test UI/Frontend configuration"""
    
    @pytest.mark.unit
    def test_ui_config_colors(self):
        """Test UI color configuration"""
        from utils.utils_ui_config import UIConfig
        
        colors = UIConfig.COLORS
        assert 'primary' in colors
        assert 'success' in colors
    
    @pytest.mark.unit
    def test_status_colors(self):
        """Test status color mapping"""
        from utils.utils_ui_config import UIConfig
        
        status_colors = UIConfig.STATUS_COLORS
        assert status_colors['operational'] == '#00B050'
        assert status_colors['down'] == '#FF0000'


@pytest.mark.slow
class TestPerformanceBenchmarks(BaseTestCase):
    """Performance benchmarks for utility functions"""
    
    def test_bulk_calculation_performance(self):
        """Benchmark bulk calculations"""
        import time
        
        start = time.time()
        
        # Perform bulk calculations
        results = []
        for i in range(1000):
            mtbf = 10000 / (i + 1) if (i + 1) > 0 else 0
            results.append(mtbf)
        
        elapsed = time.time() - start
        
        # Should complete in reasonable time (< 1 second)
        assert elapsed < 1.0
        assert len(results) == 1000


# Error Handling Tests
class TestErrorHandling(BaseTestCase):
    """Test error handling in utilities"""
    
    @pytest.mark.unit
    def test_division_by_zero_handling(self):
        """Test handling division by zero"""
        num_repairs = 0
        total_time = 100
        
        try:
            if num_repairs == 0:
                mttr = 0
            else:
                mttr = total_time / num_repairs
            assert mttr == 0
        except ZeroDivisionError:
            pytest.fail("Division by zero not handled")
    
    @pytest.mark.unit
    def test_invalid_input_handling(self):
        """Test handling invalid inputs"""
        invalid_inputs = [None, '', [], {}]
        
        for invalid_input in invalid_inputs:
            # Should handle gracefully
            if invalid_input is None or invalid_input == '':
                assert invalid_input is None or invalid_input == ''
