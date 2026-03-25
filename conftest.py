"""
pytest Configuration
Test fixtures and base test classes
"""

import os
import sys
import pytest
from typing import Generator
import tempfile
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Logging config for tests
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    db_fd, db_path = tempfile.mkstemp()
    yield db_path
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def app():
    """Create application for testing"""
    from app import create_app
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        from models import db
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Database session for tests"""
    from models import db
    with app.app_context():
        yield db.session


@pytest.fixture
def runner(app):
    """CLI runner for testing commands"""
    return app.test_cli_runner()


@pytest.fixture
def test_user(db_session):
    """Create test user"""
    from models import User
    user = User(
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User'
    )
    user.set_password('testpass123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_admin(db_session):
    """Create test admin user"""
    from models import User, Role
    user = User(
        username='admin',
        email='admin@example.com',
        is_admin=True
    )
    user.set_password('adminpass123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_project(db_session):
    """Create test project"""
    from models import Project
    project = Project(
        code='TEST_001',
        name='Test Project',
        description='Testing project',
        status='active'
    )
    db_session.add(project)
    db_session.commit()
    return project


@pytest.fixture
def test_equipment(db_session, test_project):
    """Create test equipment"""
    from models import Equipment
    equipment = Equipment(
        tram_id='TRAM_001',
        name='Test Equipment',
        equipment_type='Motor',
        project_code=test_project.code,
        status='operational',
        current_km=10000
    )
    db_session.add(equipment)
    db_session.commit()
    return equipment


# Pytest Configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


# Helper Classes
class BaseTestCase:
    """Base test case class"""
    
    def setup_method(self):
        """Setup before each test"""
        pass
    
    def teardown_method(self):
        """Cleanup after each test"""
        pass
    
    def assert_response_ok(self, response):
        """Assert response status is 200"""
        assert response.status_code == 200
    
    def assert_response_created(self, response):
        """Assert response status is 201"""
        assert response.status_code == 201
    
    def assert_response_redirect(self, response):
        """Assert response is redirect (302)"""
        assert response.status_code in [301, 302, 303, 307, 308]
    
    def assert_response_not_found(self, response):
        """Assert response is 404"""
        assert response.status_code == 404
    
    def assert_response_forbidden(self, response):
        """Assert response is 403"""
        assert response.status_code == 403
    
    def assert_response_unauthorized(self, response):
        """Assert response is 401"""
        assert response.status_code == 401


# Test Data Builders
class TestDataBuilder:
    """Helper to build test data"""
    
    @staticmethod
    def build_user(**kwargs):
        """Build user test data"""
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        return {**defaults, **kwargs}
    
    @staticmethod
    def build_equipment(**kwargs):
        """Build equipment test data"""
        defaults = {
            'tram_id': 'TRAM_001',
            'name': 'Test Equipment',
            'equipment_type': 'Motor',
            'status': 'operational',
            'current_km': 10000
        }
        return {**defaults, **kwargs}
    
    @staticmethod
    def build_failure(**kwargs):
        """Build failure test data"""
        defaults = {
            'tram_id': 'TRAM_001',
            'failure_code': 'F_001',
            'description': 'Test failure',
            'severity': 'high',
            'status': 'open'
        }
        return {**defaults, **kwargs}


# Coverage Configuration
def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add unit marker by default
        if "integration" not in item.keywords and "slow" not in item.keywords:
            item.add_marker(pytest.mark.unit)
