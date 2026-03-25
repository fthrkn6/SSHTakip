"""
Unit Tests for Database Models
Tests User, Equipment, Failure, and other core models
"""

import pytest
from conftest import BaseTestCase, TestDataBuilder


class TestUserModel(BaseTestCase):
    """Test User model"""
    
    @pytest.mark.unit
    def test_user_creation(self, test_user):
        """Test creating a user"""
        assert test_user.username == 'testuser'
        assert test_user.email == 'test@example.com'
    
    @pytest.mark.unit
    def test_user_password_hashing(self, test_user):
        """Test password hashing"""
        assert test_user.password_hash is not None
        assert test_user.password_hash != 'testpass123'
    
    @pytest.mark.unit
    def test_user_password_check(self, test_user):
        """Test password verification"""
        assert test_user.check_password('testpass123') is True
        assert test_user.check_password('wrongpassword') is False
    
    @pytest.mark.unit
    def test_user_is_admin(self, test_admin):
        """Test admin flag"""
        assert test_admin.is_admin() is True
    
    @pytest.mark.unit
    def test_user_project_access(self, db_session, test_user, test_project):
        """Test user project access"""
        # Assign project to user
        test_user.set_assigned_projects([test_project.code])
        db_session.commit()
        
        assert test_user.can_access_project(test_project.code) is True
        assert test_user.can_access_project('NONEXISTENT') is False
    
    @pytest.mark.unit
    def test_user_skills(self, test_user):
        """Test user skills"""
        test_user.skills = 'Electrical,Mechanical,Hydraulic'
        skills = test_user.get_skills_list()
        
        assert 'Electrical' in skills
        assert len(skills) == 3


class TestEquipmentModel(BaseTestCase):
    """Test Equipment model"""
    
    @pytest.mark.unit
    def test_equipment_creation(self, test_equipment):
        """Test creating equipment"""
        assert test_equipment.tram_id == 'TRAM_001'
        assert test_equipment.equipment_type == 'Motor'
        assert test_equipment.status == 'operational'
    
    @pytest.mark.unit
    def test_equipment_km_update(self, test_equipment):
        """Test updating equipment KM"""
        initial_km = test_equipment.current_km
        test_equipment.current_km = initial_km + 100
        
        assert test_equipment.current_km == initial_km + 100
    
    @pytest.mark.unit
    def test_equipment_status_change(self, test_equipment):
        """Test changing equipment status"""
        test_equipment.status = 'maintenance'
        assert test_equipment.status == 'maintenance'
        
        test_equipment.status = 'down'
        assert test_equipment.status == 'down'


class TestProjectModel(BaseTestCase):
    """Test Project model"""
    
    @pytest.mark.unit
    def test_project_creation(self, test_project):
        """Test creating project"""
        assert test_project.code == 'TEST_001'
        assert test_project.status == 'active'
    
    @pytest.mark.unit
    def test_project_equipment_relationship(self, db_session, test_project, test_equipment):
        """Test project-equipment relationship"""
        assert test_equipment.project_code == test_project.code


class TestFailureModel(BaseTestCase):
    """Test Failure model"""
    
    @pytest.mark.unit
    def test_failure_creation(self, db_session, test_equipment):
        """Test creating failure"""
        from models import Failure
        
        failure = Failure(
            tram_id=test_equipment.tram_id,
            failure_code='F_001',
            description='Motor bearing failure',
            severity='high',
            status='open'
        )
        db_session.add(failure)
        db_session.commit()
        
        assert failure.failure_code == 'F_001'
        assert failure.severity == 'high'
    
    @pytest.mark.unit
    def test_failure_status_lifecycle(self, db_session, test_equipment):
        """Test failure status changes"""
        from models import Failure
        
        failure = Failure(
            tram_id=test_equipment.tram_id,
            failure_code='F_002',
            description='Test failure',
            severity='medium',
            status='open'
        )
        db_session.add(failure)
        db_session.commit()
        
        # Change status
        failure.status = 'in_progress'
        db_session.commit()
        assert failure.status == 'in_progress'
        
        # Close failure
        failure.status = 'closed'
        db_session.commit()
        assert failure.status == 'closed'


class TestMaintenancePlanModel(BaseTestCase):
    """Test MaintenancePlan model"""
    
    @pytest.mark.unit
    def test_maintenance_plan_creation(self, db_session, test_equipment):
        """Test creating maintenance plan"""
        from models import MaintenancePlan
        from datetime import datetime, timedelta
        
        plan = MaintenancePlan(
            tram_id=test_equipment.tram_id,
            plan_type='preventive',
            planned_date=(datetime.now() + timedelta(days=30)).date(),
            description='Monthly preventive inspection'
        )
        db_session.add(plan)
        db_session.commit()
        
        assert plan.plan_type == 'preventive'
        assert plan.status == 'pending'


class TestRolePermissionModel(BaseTestCase):
    """Test Role and Permission models"""
    
    @pytest.mark.unit
    def test_role_creation(self, db_session):
        """Test creating role"""
        from models import Role
        
        role = Role(
            name='Technician',
            description='Field technician'
        )
        db_session.add(role)
        db_session.commit()
        
        assert role.name == 'Technician'
    
    @pytest.mark.unit
    def test_permission_creation(self, db_session):
        """Test creating permission"""
        from models import Permission
        
        permission = Permission(
            name='view_failures',
            description='Can view failure reports'
        )
        db_session.add(permission)
        db_session.commit()
        
        assert permission.name == 'view_failures'
    
    @pytest.mark.unit
    def test_role_permission_relationship(self, db_session):
        """Test role-permission assignment"""
        from models import Role, Permission, RolePermission
        
        role = Role(name='Manager')
        permission = Permission(name='approve_work_orders')
        
        db_session.add(role)
        db_session.add(permission)
        db_session.commit()
        
        role_perm = RolePermission(role_id=role.id, permission_id=permission.id)
        db_session.add(role_perm)
        db_session.commit()
        
        assert role_perm.role_id == role.id
        assert role_perm.permission_id == permission.id


# Benchmark Tests
@pytest.mark.slow
class TestModelBenchmarks(BaseTestCase):
    """Benchmark model operations"""
    
    def test_bulk_equipment_creation(self, db_session):
        """Benchmark bulk equipment creation"""
        from models import Equipment, Project
        
        # Create test project
        project = Project(code='BENCH_001', name='Benchmark')
        db_session.add(project)
        db_session.commit()
        
        # Bulk create equipment
        equipment_list = [
            Equipment(
                tram_id=f'TRAM_{i:04d}',
                name=f'Equipment {i}',
                equipment_type='Motor',
                project_code=project.code,
                current_km=i * 1000
            )
            for i in range(100)
        ]
        
        db_session.bulk_save_objects(equipment_list)
        db_session.commit()
        
        # Verify
        count = db_session.query(Equipment).filter_by(project_code=project.code).count()
        assert count == 100
