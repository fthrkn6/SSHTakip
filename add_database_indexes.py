"""
Database Indexing Migration
Adds indexes to frequently queried columns for performance optimization
Run with: python add_database_indexes.py
"""

from models import db, Equipment, Failure, MaintenancePlan, WorkOrder, ServiceLog, User, Role, Permission
from flask import current_app
import time

def add_indexes():
    """Add performance indexes to database tables"""
    
    indexes_to_create = [
        # Equipment indexes
        ('equipment', 'project_code'),
        ('equipment', 'is_active'),
        ('equipment', 'status'),
        ('equipment', 'created_date'),
        ('equipment', 'equipment_type'),
        
        # Failure indexes
        ('failure', 'equipment_id'),
        ('failure', 'project_code'),
        ('failure', 'failure_date'),
        ('failure', 'failure_class_id'),
        ('failure', 'status'),
        ('failure', 'created_date'),
        ('failure', 'assigned_to_id'),
        
        # Maintenance Plan indexes
        ('maintenance_plan', 'equipment_id'),
        ('maintenance_plan', 'project_code'),
        ('maintenance_plan', 'planned_start'),
        ('maintenance_plan', 'planned_end'),
        ('maintenance_plan', 'status'),
        ('maintenance_plan', 'assigned_to_id'),
        
        # Work Order indexes
        ('work_order', 'failure_id'),
        ('work_order', 'maintenance_plan_id'),
        ('work_order', 'project_code'),
        ('work_order', 'created_date'),
        ('work_order', 'status'),
        ('work_order', 'assigned_to_id'),
        
        # Service Log indexes
        ('service_log', 'equipment_id'),
        ('service_log', 'project_code'),
        ('service_log', 'log_date'),
        ('service_log', 'created_date'),
        
        # User indexes
        ('user', 'username'),
        ('user', 'email'),
        ('user', 'is_active'),
        ('user', 'role_id'),
    ]
    
    created_count = 0
    skipped_count = 0
    
    print("\n" + "="*60)
    print("DATABASE INDEX MIGRATION")
    print("="*60 + "\n")
    
    for table_name, column_name in indexes_to_create:
        index_name = f"idx_{table_name}_{column_name}"
        
        try:
            # Create index using raw SQL
            sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})"
            db.session.execute(sql)
            db.session.commit()
            
            print(f"✅ Created index: {index_name}")
            created_count += 1
            time.sleep(0.1)  # Small delay to avoid overwhelming DB
            
        except Exception as e:
            if 'already exists' in str(e) or 'duplicate' in str(e).lower():
                print(f"⏭️  Skipped (already exists): {index_name}")
                skipped_count += 1
            else:
                print(f"❌ Failed to create {index_name}: {str(e)}")
    
    print("\n" + "="*60)
    print(f"MIGRATION SUMMARY")
    print("="*60)
    print(f"✅ Created indexes: {created_count}")
    print(f"⏭️  Skipped (existing): {skipped_count}")
    print(f"📊 Total processed: {created_count + skipped_count}")
    print("="*60 + "\n")
    
    return created_count, skipped_count


def add_composite_indexes():
    """Add composite indexes for common query patterns"""
    
    composite_indexes = [
        # (table, columns, index_name)
        ('equipment', ['project_code', 'is_active'], 'idx_equipment_project_active'),
        ('failure', ['equipment_id', 'failure_date'], 'idx_failure_equipment_date'),
        ('failure', ['project_code', 'status', 'failure_date'], 'idx_failure_project_status_date'),
        ('maintenance_plan', ['equipment_id', 'status'], 'idx_maintenance_equipment_status'),
        ('work_order', ['failure_id', 'status'], 'idx_workorder_failure_status'),
        ('service_log', ['equipment_id', 'log_date'], 'idx_servicelog_equipment_date'),
    ]
    
    created_count = 0
    
    print("\n" + "="*60)
    print("COMPOSITE INDEX MIGRATION")
    print("="*60 + "\n")
    
    for table_name, columns, index_name in composite_indexes:
        columns_str = ','.join(columns)
        
        try:
            sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({columns_str})"
            db.session.execute(sql)
            db.session.commit()
            
            print(f"✅ Created composite index: {index_name}")
            print(f"   Columns: {columns_str}")
            created_count += 1
            time.sleep(0.1)
            
        except Exception as e:
            if 'already exists' in str(e) or 'duplicate' in str(e).lower():
                print(f"⏭️  Skipped (already exists): {index_name}")
            else:
                print(f"❌ Failed to create {index_name}: {str(e)}")
    
    print("\n" + "="*60)
    print(f"COMPOSITE INDEX SUMMARY")
    print("="*60)
    print(f"✅ Created indexes: {created_count}")
    print("="*60 + "\n")
    
    return created_count


def verify_indexes():
    """Verify that indexes were created"""
    
    print("\n" + "="*60)
    print("INDEX VERIFICATION")
    print("="*60 + "\n")
    
    # This is database-specific; for SQLite:
    # For PostgreSQL, would use pg_indexes
    # For MySQL, would use INFORMATION_SCHEMA
    
    try:
        # Get all indexes (SQLite)
        result = db.session.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name LIKE 'idx_%'
            ORDER BY name
        """)
        
        indexes = result.fetchall()
        print(f"Found {len(indexes)} indexes:\n")
        
        for idx_row in indexes:
            idx_name = idx_row[0] if isinstance(idx_row, tuple) else idx_row
            print(f"  📍 {idx_name}")
        
        print("\n" + "="*60 + "\n")
        return len(indexes)
        
    except Exception as e:
        print(f"⚠️  Could not verify indexes: {str(e)}")
        print("(This is normal for some database backends)")
        print("="*60 + "\n")
        return 0


def get_index_recommendations():
    """Provide indexing recommendations based on query patterns"""
    
    recommendations = {
        'HIGH_PRIORITY': [
            {
                'reason': 'Frequently filtered on project_code',
                'table': 'equipment, failure, maintenance_plan',
                'recommended_index': 'idx_table_project_code'
            },
            {
                'reason': 'Filter by status in many queries',
                'table': 'failure, work_order, maintenance_plan',
                'recommended_index': 'idx_table_status'
            },
            {
                'reason': 'Date range queries for reporting',
                'table': 'failure, service_log',
                'recommended_index': 'idx_table_created_date'
            },
        ],
        'MEDIUM_PRIORITY': [
            {
                'reason': 'Join with equipment table',
                'table': 'failure, maintenance_plan, work_order',
                'recommended_index': 'idx_table_equipment_id'
            },
            {
                'reason': 'Filter by is_active status',
                'table': 'equipment, user',
                'recommended_index': 'idx_table_is_active'
            },
        ],
        'COMPOSITE_INDEXES': [
            {
                'reason': 'Common filter combination',
                'columns': '(project_code, status)',
                'tables': 'failure, work_order'
            },
            {
                'reason': 'Equipment + date range queries',
                'columns': '(equipment_id, created_date)',
                'tables': 'service_log, km_log'
            },
        ]
    }
    
    return recommendations


# CLI execution
if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        print("\n🔧 Starting database index migration...\n")
        
        # Add primary indexes
        created, skipped = add_indexes()
        
        # Add composite indexes
        composite_created = add_composite_indexes()
        
        # Verify indexes
        total_indexes = verify_indexes()
        
        # Show recommendations
        print("📋 INDEXING RECOMMENDATIONS:")
        print("="*60)
        recs = get_index_recommendations()
        
        print("\n🔴 HIGH PRIORITY:")
        for rec in recs['HIGH_PRIORITY']:
            print(f"  • {rec['reason']}")
            print(f"    Tables: {rec['table']}")
            print(f"    Index: {rec['recommended_index']}\n")
        
        print("\n🟡 MEDIUM PRIORITY:")
        for rec in recs['MEDIUM_PRIORITY']:
            print(f"  • {rec['reason']}")
            print(f"    Tables: {rec['table']}")
            print(f"    Index: {rec['recommended_index']}\n")
        
        print("="*60)
        print(f"\n✅ Migration completed!")
        print(f"   Total indexes created: {created + composite_created}")
        print(f"   Database ready for optimization!\n")
