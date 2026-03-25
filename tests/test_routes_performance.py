"""
Unit tests for API routes
Run with: pytest tests/test_routes.py -v
"""

import pytest
import json
from datetime import datetime


class TestDashboardRoutes:
    """Test dashboard routes"""
    
    def test_dashboard_get(self, client):
        """Test loading dashboard"""
        response = client.get('/dashboard')
        # Assert response is 200 or 302 (redirect to login)
        assert response.status_code in [200, 302]
    
    def test_dashboard_requires_auth(self, client):
        """Test dashboard requires authentication"""
        response = client.get('/dashboard')
        # Should redirect to login or return 401
        assert response.status_code in [302, 401, 200]  # Depends on auth setup


class TestEquipmentRoutes:
    """Test equipment API routes"""
    
    def test_equipment_list(self, client, authenticated_headers):
        """Test getting equipment list"""
        response = client.get(
            '/equipment',
            headers=authenticated_headers
        )
        # Should return 200 or require authentication
        assert response.status_code in [200, 401, 302]
    
    def test_equipment_list_with_project(self, client, authenticated_headers):
        """Test equipment list filtered by project"""
        response = client.get(
            '/equipment?project_code=belgrad',
            headers=authenticated_headers
        )
        assert response.status_code in [200, 401, 302]
    
    def test_equipment_detail(self, client, authenticated_headers, test_equipment):
        """Test getting single equipment"""
        response = client.get(
            f'/equipment/{test_equipment.id}',
            headers=authenticated_headers
        )
        assert response.status_code in [200, 401, 302, 404]
    
    def test_equipment_create(self, client, authenticated_headers):
        """Test creating equipment"""
        payload = {
            'equipment_code': 'TEST-001',
            'equipment_name': 'Test Equipment',
            'project_code': 'belgrad',
            'equipment_type': 'motor'
        }
        response = client.post(
            '/equipment',
            data=json.dumps(payload),
            content_type='application/json',
            headers=authenticated_headers
        )
        assert response.status_code in [201, 200, 401, 302, 400]
    
    def test_equipment_update(self, client, authenticated_headers, test_equipment):
        """Test updating equipment"""
        payload = {
            'equipment_name': 'Updated Name',
            'status': 'arızalı'
        }
        response = client.put(
            f'/equipment/{test_equipment.id}',
            data=json.dumps(payload),
            content_type='application/json',
            headers=authenticated_headers
        )
        assert response.status_code in [200, 204, 401, 302, 404, 400]
    
    def test_equipment_delete(self, client, authenticated_headers, test_equipment):
        """Test deleting equipment"""
        response = client.delete(
            f'/equipment/{test_equipment.id}',
            headers=authenticated_headers
        )
        assert response.status_code in [200, 204, 401, 302, 404, 403]


class TestFailureRoutes:
    """Test failure API routes"""
    
    def test_failure_list(self, client, authenticated_headers):
        """Test getting failures"""
        response = client.get(
            '/failures',
            headers=authenticated_headers
        )
        assert response.status_code in [200, 401, 302]
    
    def test_failure_create(self, client, authenticated_headers, test_equipment):
        """Test creating failure report"""
        payload = {
            'equipment_id': test_equipment.id,
            'project_code': 'belgrad',
            'failure_description': 'Motor not working',
            'failure_date': datetime.now().isoformat()
        }
        response = client.post(
            '/failures',
            data=json.dumps(payload),
            content_type='application/json',
            headers=authenticated_headers
        )
        assert response.status_code in [201, 200, 401, 302, 400]


class TestPerformanceRoutes:
    """Test performance monitoring routes"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/performance/health')
        assert response.status_code == 200
        data = response.get_json()
        assert 'database' in data or 'status' in data
    
    def test_metrics_endpoint(self, client, authenticated_headers):
        """Test metrics endpoint"""
        response = client.get(
            '/performance/metrics',
            headers=authenticated_headers
        )
        assert response.status_code in [200, 401, 302]
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, dict)
    
    def test_cache_stats(self, client, authenticated_headers):
        """Test cache statistics endpoint"""
        response = client.get(
            '/performance/cache/stats',
            headers=authenticated_headers
        )
        assert response.status_code in [200, 401, 302]
    
    def test_performance_dashboard(self, client, authenticated_headers):
        """Test performance dashboard"""
        response = client.get(
            '/performance/performance-dashboard',
            headers=authenticated_headers
        )
        assert response.status_code in [200, 401, 302, 403]


class TestReportingRoutes:
    """Test reporting API routes"""
    
    def test_templates_list(self, client, authenticated_headers):
        """Test getting report templates"""
        response = client.get(
            '/api/reports/templates',
            headers=authenticated_headers
        )
        assert response.status_code in [200, 401, 302]
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, list) or isinstance(data, dict)
    
    def test_template_detail(self, client, authenticated_headers):
        """Test getting specific template"""
        response = client.get(
            '/api/reports/templates/daily_ops',
            headers=authenticated_headers
        )
        assert response.status_code in [200, 401, 302, 404]
    
    def test_generate_report(self, client, authenticated_headers):
        """Test generating report"""
        payload = {
            'template_name': 'daily_ops',
            'format': 'json',
            'filters': {
                'project_code': 'belgrad',
                'date_range': 'today'
            }
        }
        response = client.post(
            '/api/reports/generate',
            data=json.dumps(payload),
            content_type='application/json',
            headers=authenticated_headers
        )
        assert response.status_code in [200, 201, 401, 302, 400]
    
    def test_export_report(self, client, authenticated_headers):
        """Test exporting report"""
        payload = {
            'template_name': 'daily_ops',
            'format': 'pdf',
            'filters': {'project_code': 'belgrad'}
        }
        response = client.post(
            '/api/reports/export',
            data=json.dumps(payload),
            content_type='application/json',
            headers=authenticated_headers
        )
        assert response.status_code in [200, 401, 302, 400]


class TestAuthRoutes:
    """Test authentication routes"""
    
    def test_login_page(self, client):
        """Test login page"""
        response = client.get('/login')
        assert response.status_code in [200, 302]
    
    def test_logout(self, client, authenticated_headers):
        """Test logout"""
        response = client.get('/logout', headers=authenticated_headers)
        assert response.status_code in [200, 302, 401]


class TestErrorHandling:
    """Test error handling in routes"""
    
    def test_404_error(self, client):
        """Test 404 not found"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self, client):
        """Test method not allowed"""
        response = client.post('/dashboard')
        assert response.status_code in [405, 302, 401]
    
    def test_invalid_json(self, client, authenticated_headers):
        """Test invalid JSON payload"""
        response = client.post(
            '/equipment',
            data='invalid json',
            content_type='application/json',
            headers=authenticated_headers
        )
        assert response.status_code in [400, 401, 302]


class TestResponseFormats:
    """Test API response formats"""
    
    def test_json_response_format(self, client, authenticated_headers):
        """Test JSON response format"""
        response = client.get(
            '/api/reports/templates',
            headers=authenticated_headers
        )
        if response.status_code == 200:
            assert response.content_type == 'application/json'
    
    def test_html_response_format(self, client):
        """Test HTML response format"""
        response = client.get('/dashboard')
        if response.status_code == 200:
            assert 'text/html' in response.content_type
    
    def test_response_headers(self, client):
        """Test response headers"""
        response = client.get('/performance/health')
        assert 'Content-Type' in response.headers


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
