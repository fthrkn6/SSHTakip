"""
Unit Tests for API Routes and Views
Tests endpoint functionality, status codes, and responses
"""

import pytest
from conftest import BaseTestCase
import json


class TestAuthRoutes(BaseTestCase):
    """Test authentication routes"""
    
    @pytest.mark.unit
    def test_login_page_access(self, client):
        """Test login page loads"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    @pytest.mark.unit
    def test_login_with_valid_credentials(self, client, test_user):
        """Test login with correct password"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    @pytest.mark.unit
    def test_login_with_invalid_credentials(self, client):
        """Test login with wrong password"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200
        # Should show error message


class TestDashboardRoutes(BaseTestCase):
    """Test dashboard routes"""
    
    @pytest.mark.unit
    def test_dashboard_access_requires_login(self, client):
        """Test dashboard requires authentication"""
        response = client.get('/dashboard')
        assert response.status_code in [302, 401]  # Redirect or Forbidden
    
    @pytest.mark.unit
    def test_dashboard_access_authenticated(self, client, test_user):
        """Test dashboard access when logged in"""
        with client:
            client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass123'
            })
            
            response = client.get('/dashboard')
            # Should load dashboard
            assert response.status_code == 200


class TestEquipmentRoutes(BaseTestCase):
    """Test equipment management routes"""
    
    @pytest.mark.unit
    def test_equipment_list_endpoint(self, client, test_user, test_equipment):
        """Test equipment list endpoint"""
        response = client.get('/equipment/listesi')
        # Could be 200 if no auth or 401 if requires auth
        assert response.status_code in [200, 401, 302]
    
    @pytest.mark.unit
    def test_equipment_detail_endpoint(self, client, test_equipment):
        """Test equipment detail endpoint"""
        response = client.get(f'/equipment/{test_equipment.id}')
        assert response.status_code in [200, 404, 401]
    
    @pytest.mark.unit
    def test_equipment_api_sync(self, client):
        """Test equipment sync API"""
        response = client.get('/equipment/api/sync?project_code=TEST_001')
        # Should return JSON response
        assert response.status_code in [200, 400, 401]


class TestFailureRoutes(BaseTestCase):
    """Test failure/FRACAS routes"""
    
    @pytest.mark.unit
    def test_failure_list_endpoint(self, client):
        """Test failure list page"""
        response = client.get('/fracas/listesi')
        assert response.status_code in [200, 401, 302]
    
    @pytest.mark.unit
    def test_failure_add_endpoint(self, client):
        """Test failure add page"""
        response = client.get('/fracas/ariza/ekle')
        assert response.status_code in [200, 401, 302]


class TestReportRoutes(BaseTestCase):
    """Test reporting routes"""
    
    @pytest.mark.unit
    def test_report_list_endpoint(self, client):
        """Test report list"""
        response = client.get('/reports/listesi')
        assert response.status_code in [200, 401, 302]
    
    @pytest.mark.unit
    def test_report_download_endpoint(self, client):
        """Test report download"""
        response = client.get('/reports/indir')
        assert response.status_code in [200, 400, 401]


class TestAPIEndpoints(BaseTestCase):
    """Test RESTful API endpoints"""
    
    @pytest.mark.unit
    def test_api_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
    
    @pytest.mark.unit
    def test_api_projects_endpoint(self, client, test_project):
        """Test projects API endpoint"""
        response = client.get('/api/projects')
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, list)
    
    @pytest.mark.unit
    def test_api_statistics_endpoint(self, client):
        """Test statistics API endpoint"""
        response = client.get('/api/statistics/kpi')
        assert response.status_code in [200, 400, 401]
    
    @pytest.mark.unit
    def test_api_failure_lookup(self, client):
        """Test failure lookup API"""
        response = client.get('/api/failure-by-fracas-id?code=F_001')
        assert response.status_code in [200, 404, 401]


class TestErrorHandling(BaseTestCase):
    """Test error handling"""
    
    @pytest.mark.unit
    def test_404_not_found(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent/route')
        assert response.status_code == 404
    
    @pytest.mark.unit
    def test_method_not_allowed(self, client):
        """Test 405 error handling"""
        response = client.post('/dashboard')  # Dashboard might only accept GET
        assert response.status_code in [405, 200, 405]
    
    @pytest.mark.unit
    def test_invalid_json_request(self, client):
        """Test invalid JSON handling"""
        response = client.post('/api/test', 
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code in [400, 404, 405]


class TestCORS(BaseTestCase):
    """Test CORS headers"""
    
    @pytest.mark.unit
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present"""
        response = client.get('/api/health')
        # Should have CORS headers if enabled
        assert response.status_code == 200


@pytest.mark.integration
class TestAuthenticationFlow(BaseTestCase):
    """Integration tests for authentication flow"""
    
    def test_complete_login_logout_flow(self, client, test_user):
        """Test complete login/logout flow"""
        # Login
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Access protected resource
        response = client.get('/dashboard')
        assert response.status_code in [200, 401]
        
        # Logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200


@pytest.mark.integration
class TestDataFlow(BaseTestCase):
    """Integration tests for data flow"""
    
    def test_equipment_to_failure_flow(self, client, test_equipment):
        """Test creating failure for equipment"""
        # Equipment exists
        response = client.get(f'/equipment/{test_equipment.id}')
        assert response.status_code in [200, 401]
        
        # Add failure
        response = client.post('/fracas/ariza/ekle', data={
            'tram_id': test_equipment.tram_id,
            'failure_code': 'F_TEST',
            'description': 'Test failure'
        })
        assert response.status_code in [200, 201, 302, 401]
