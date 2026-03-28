# 🗄️ BOZANKAYA CMS - DATABASE ARCHITECTURE

**Status**: CMSv1.1 Base Architecture  
**Database**: SQLite (Development) | PostgreSQL Ready (Production)  
**Tables**: 20+ core + 5 utility tables  
**Records**: 1000+ (7 projects combined)

---

## 📐 DATABASE SCHEMA DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CMMS DATABASE (ssh_takip_bozankaya.db)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     USER MANAGEMENT DOMAIN                         │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                     │   │
│  │  ┌──────────────┐         ┌──────────────┐       ┌─────────────┐   │   │
│  │  │    ROLE      │◄────┬───┤     USER     ├──────►│  PERMISSION │   │   │
│  │  ├──────────────┤     │   ├──────────────┤       ├─────────────┤   │   │
│  │  │ id●          │     │   │ id●          │       │ id●         │   │   │
│  │  │ name         │     │   │ username     │       │ page_name   │   │   │
│  │  │ permissions  │     │   │ email        │       │ description │   │   │
│  │  │ created_at   │     │   │ password_hash│       │ category    │   │   │
│  │  └──────────────┘     │   │ full_name    │       └─────────────┘   │   │
│  │                       │   │ role_id (FK) │                         │   │
│  │                       │   │ role (legacy)│                         │   │
│  │  ┌──────────────┐     │   │ assigned_    │       ┌──────────────┐   │   │
│  │  │ROLE_         │◄────┘   │  projects    │       │   AUDIT      │   │   │
│  │  │PERMISSION    │         │ department   │      │    LOG       │   │   │
│  │  ├──────────────┤         │ skills (JSON)│       ├──────────────┤   │   │
│  │  │ role (FK)    │         │ created_at   │       │ id●          │   │   │
│  │  │ permission_id│         └──────────────┘       │ user_id      │   │   │
│  │  │ (composite   │                                │ action       │   │   │
│  │  │  primary key)│                                │ table        │   │   │
│  │  └──────────────┘                                │ timestamp    │   │   │
│  │                                                    └──────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                    ASSET MANAGEMENT DOMAIN (Core)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                                                                    │    │
│  │  ┌──────────────┐                    ┌───────────────────┐        │    │
│  │  │  EQUIPMENT   │◄──────────────────►│  METER_READING    │        │    │
│  │  ├──────────────┤                    ├───────────────────┤        │    │
│  │  │ id● (PK)     │                    │ id●               │        │    │
│  │  │ code (unique)│ 1                ◄─┤ equipment_id (FK) │        │    │
│  │  │ name         │  \  ┌─────────┐   │ reading_date      │        │    │
│  │  │ type         │   ──┤ FAILURE │   │ km_value          │        │    │
│  │  │ project_code │  /  │ (1:Many)│   │ hours_value       │        │    │
│  │  │ status       │ 1    └─────────┘   │ notes             │        │    │
│  │  │ current_km   │  \   ┌───────────┐ └───────────────────┘        │    │
│  │  │ mtbf_hours   │   ──┤ WORK_ORDER│                              │    │
│  │  │ mttr_hours   │  /   │  (1:Many) │ ┌───────────────────┐       │    │
│  │  │ availability │ 1    └───────────┘ │MAINT_PLAN         │       │    │
│  │  │ criticality  │  \   ┌────────────┐├───────────────────┤       │    │
│  │  │ parent_id (FK)   ──┤SPARE_PART  │ │ id●               │       │    │
│  │  │ (hierarchy) │  /    │INVENTORY  │ │ equipment_id (FK) │       │    │
│  │  │ created_at  │ 1     └────────────┘ │ type              │       │    │
│  │  └──────────────┘                     │ frequency_type    │       │    │
│  │       ▲                                │ frequency_value   │       │    │
│  │       │ (1:Many)                      │ next_due_date     │       │    │
│  │       │ (hierarchy)                    │ is_active         │       │    │
│  │       │                                └───────────────────┘       │    │
│  │  (Self-referential for                                             │    │
│  │   Tren > Subsystem > Part)           ┌──────────────────┐        │    │
│  │                                       │ DOWNTIME_RECORD  │        │    │
│  │                                       ├──────────────────┤        │    │
│  │                                       │ id●              │        │    │
│  │  ┌──────────────────┐                │ equipment_id (FK)│        │    │
│  │  │ AVAILABILITY     │                │ start_time       │        │    │
│  │  │ METRICS          │                │ end_time         │        │    │
│  │  ├──────────────────┤                │ duration_minutes │        │    │
│  │  │ id●              │                │ type             │        │    │
│  │  │ equipment_id (FK)│                │ reason           │        │    │
│  │  │ date             │                └──────────────────┘        │    │
│  │  │ availability_%   │                                             │    │
│  │  │ planned_downtime │                                             │    │
│  │  │ unplanned_...    │                                             │    │
│  │  │ total_uptime     │                                             │    │
│  │  └──────────────────┘                                             │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                    FAILURE & MAINTENANCE DOMAIN                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │                                                              │          │
│  │  ┌──────────────┐        ┌─────────────────────┐           │          │
│  │  │  FAILURE     │───────►│ROOT_CAUSE_ANALYSIS  │           │          │
│  │  ├──────────────┤1      ◄─├─────────────────────┤           │          │
│  │  │ id●          │         │ id●                 │           │          │
│  │  │ code (unique)│    1    │ failure_id (FK)     │           │          │
│  │  │ equipment_id │────┐    │ root_cause          │           │          │
│  │  │ title        │    │    │ corrective_actions  │           │          │
│  │  │ description  │    │    │ preventive_actions  │           │          │
│  │  │ severity     │    │    │ analyzed_by (USER FK)           │          │
│  │  │ status       │    │    │ analysis_date       │           │          │
│  │  │ failure_type │    │    │ created_at          │           │          │
│  │  │ detected_date│    │    └─────────────────────┘           │          │
│  │  │ resolved_date│    │                                      │          │
│  │  │ downtime_min │    │    ┌──────────────────┐             │          │
│  │  │ repair_cost  │    └───►│ WORK_ORDER       │             │          │
│  │  │ project_code │    1    ├──────────────────┤             │          │
│  │  │ created_at   │         │ id●              │             │          │
│  │  └──────────────┘         │ code             │             │          │
│  │                           │ equipment_id (FK)│             │          │
│  │  ┌──────────────┐         │ title            │             │          │
│  │  │ SERVICE_LOG  │         │ priority         │             │          │
│  │  ├──────────────┤         │ status           │             │          │
│  │  │ id●          │         │ scheduled_date   │             │          │
│  │  │ equipment_id │         │ assigned_to (FK) │             │          │
│  │  │ service_date │         │ estimated_hours  │             │          │
│  │  │ service_type │         │ actual_hours     │             │          │
│  │  │ notes        │         │ created_at       │             │          │
│  │  │ created_by   │         └──────────────────┘             │          │
│  │  │ created_at   │                                          │          │
│  │  └──────────────┘         ┌──────────────────┐             │          │
│  │                           │ SPARE_PART       │             │          │
│  │                           │ INVENTORY        │             │          │
│  │                           ├──────────────────┤             │          │
│  │                           │ id●              │             │          │
│  │                           │ equipment_id (FK)│             │          │
│  │                           │ part_code        │             │          │
│  │                           │ part_name        │             │          │
│  │                           │ unit_cost        │             │          │
│  │                           │ quantity_on_hand │             │          │
│  │                           │ quantity_reserved│             │          │
│  │                           │ reorder_level    │             │          │
│  │                           │ lead_time_days   │             │          │
│  │                           └──────────────────┘             │          │
│  │                                                              │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                    DOCUMENTATION & CONFIG DOMAIN                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐   ┌────────────────┐          │
│  │TECHNICAL_        │  │ MAINTENANCE_     │   │SECURITY_       │          │
│  │DOCUMENT          │  │SPECIFICATION     │   │INCIDENT        │          │
│  ├──────────────────┤  ├──────────────────┤   ├────────────────┤          │
│  │ id●              │  │ id●              │   │ id●            │          │
│  │ equipment_id(FK) │  │ equipment_id(FK) │   │ incident_code  │          │
│  │ file_path        │  │ version          │   │ incident_type  │          │
│  │ file_name        │  │ specification    │   │ severity       │          │
│  │ document_type    │  │ updated_at       │   │ status         │          │
│  │ uploaded_by(FK)  │  │ updated_by(FK)   │   │ detected_at    │          │
│  │ uploaded_at      │  └──────────────────┘   │ resolved_at    │          │
│  │ notes            │                         │ reported_by(FK)│          │
│  └──────────────────┘                         │ assigned_to(FK)│          │
│                                               └────────────────┘          │
│  ┌──────────────────────────────────────────────────────┐                │
│  │ PROJECT_CONFIG (Configuration Table)                 │                │
│  ├──────────────────────────────────────────────────────┤                │
│  │ id●                                                  │                │
│  │ project_code (unique)  → belgrad, kayseri, istanbul │                │
│  │ project_name           → Full name                   │                │
│  │ location               → Geographic location         │                │
│  │ vehicle_count          → Number of trams             │                │
│  │ settings (JSON)        → Project-specific settings   │                │
│  │ created_at             → Setup date                  │                │
│  └──────────────────────────────────────────────────────┘                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 VERİ AKIŞI DOMAIN'LERE GÖRE

### 1️⃣ USER MANAGEMENT DOMAIN

**Amaç**: Kimlik doğrulama, rol yönetimi, izin kontrolü

**Tablolar**:
```
┌─────────────────────────────────────────┐
│ Tablolar                  │ Relationships│
├─────────────────────────────────────────┤
│ User                      │ 1→Many User │
│ Role                      │ 1→Many Role │
│ Permission                │ M→N via Role│
│ RolePermission            │ Junction    │
│ AuditLog                  │ 1→Many User │
└─────────────────────────────────────────┘
```

**Key Operations**:
- User login (SQL: SELECT password_hash FROM user WHERE username)
- Permission check (SQL: SELECT permission FROM role_permission WHERE role)
- Project access (JSON parse: user.assigned_projects)
- Create user (INSERT into user + UPDATE role)

---

### 2️⃣ ASSET MANAGEMENT DOMAIN

**Amaç**: Ekipman envanteri, takip, sağlık yönetimi

**Tablolar**:
```
Equipment (ROOT)
├── Meter Reading          (1→Many)
├── Downtime Record        (1→Many)
├── Availability Metrics   (1→Many)
├── Spare Part Inventory   (1→Many)
├── Maintenance Plan       (1→Many)
├── Equipment (SELF)       (1→Many - hierarchy)
└── Failure                (1→Many)
```

**Key Operations**:
- List equipment: `SELECT * FROM equipment WHERE project_code = 'belgrad'` (50-100 ms)
- Get equipment details: `SELECT * FROM equipment WHERE id = X` + relationships
- Calculate availability: `(total_minutes - SUM(downtime)) / total_minutes * 100`
- Hierarchy traversal: Recursive CTE (equipment.parent_id)

---

### 3️⃣ FAILURE & MAINTENANCE DOMAIN

**Amaç**: Arıza takip, kök neden analizi, süveyliş

**Tablolar**:
```
Failure (ROOT)
├── Work Order             (1→Many)
├── Root Cause Analysis    (1→1)
└── Service Log            (Many→1)
```

**Key Operations**:
- List failures: `SELECT * FROM failure WHERE project_code = 'belgrad' ORDER BY created_at DESC`
- Recent failures by equipment: `SELECT * FROM failure WHERE equipment_id = X LIMIT 5`
- MTTR calculation: `AVG(downtime_minutes) WHERE status = 'cozuldu'`
- Failure trend: `SELECT DATE(created_at) as date, COUNT(*) FROM failure GROUP BY date`

---

## 🔗 CRITICAL RELATIONSHIPS

### Equipment → Failure (Primary Chain)

```sql
-- Get equipment with failure count
SELECT 
  e.equipment_code,
  e.name,
  COUNT(f.id) as failure_count,
  AVG(f.downtime_minutes) as avg_mttr_minutes
FROM equipment e
LEFT JOIN failure f ON e.id = f.equipment_id
WHERE e.project_code = 'belgrad'
GROUP BY e.id
ORDER BY failure_count DESC;
```

### Equipment → Maintenance Plan (Predictive)

```sql
-- Get overdue maintenance plans
SELECT 
  e.equipment_code,
  mp.maintenance_code,
  mp.next_due_date,
  JULIANDAY('now') - JULIANDAY(mp.next_due_date) as days_overdue
FROM equipment e
JOIN maintenance_plan mp ON e.id = mp.equipment_id
WHERE mp.is_active = 1
  AND mp.next_due_date < date('now')
  AND e.project_code = 'belgrad'
ORDER BY days_overdue DESC;
```

---

## 📊 TABLE STATISTICS (CMSv1.1 Base)

```
┌──────────────────┬──────────┬──────────┬────────────┐
│ Table Name       │ Records  │ Est. Size│ Index Recommendation │
├──────────────────┼──────────┼──────────┼────────────┤
│ Equipment        │ 100-150  │ ~150 KB  │ (project_code, status) │
│ Failure          │ 200-500  │ ~500 KB  │ (equipment_id, status) │
│ ServiceLog       │ 800+ │    ~2 MB     │ (equipment_id, date)   │
│ User             │ 20-30    │ ~50 KB   │ (username), (email)    │
│ WorkOrder        │ 100-300  │ ~200 KB  │ (equipment_id, status) │
│ MaintenancePlan  │ 50-150   │ ~80 KB   │ (equipment_id)         │
│ MeterReading     │ 500+│     ~300 KB   │ (equipment_id, date)   │
│ DowntimeRecord   │ 1000+    │ ~500 KB  │ (equipment_id, date)   │
│ AuditLog         │ 5000+    │ ~1 MB    │ (table_name, timestamp)│
│ (10+ other)      │ Varies   │ ~2 MB    │ As needed              │
├──────────────────┼──────────┼──────────┼────────────┤
│ TOTAL            │ ~3000-4000 records │ ~8-10 MB             │
└──────────────────┴──────────┴──────────┴────────────┘
```

---

## ⚡ QUERY PERFORMANCE TUNING

### Missing Indexes (CMSv1.1)

```python
# App.py should execute:

# 1. Equipment lookups
db.execute("""
CREATE INDEX IF NOT EXISTS idx_equipment_project_status
ON equipment(project_code, status);
""")

# 2. Failure queries
db.execute("""
CREATE INDEX IF NOT EXISTS idx_failure_equipment_status
ON failure(equipment_id, status);
""")

# 3. Service logs
db.execute("""
CREATE INDEX IF NOT EXISTS idx_service_log_equipment_date
ON service_log(equipment_id, service_date);
""")

# 4. Downtime tracking
db.execute("""
CREATE INDEX IF NOT EXISTS idx_downtime_equipment_date
ON downtime_record(equipment_id, start_time);
""")

# 5. Maintenance planning
db.execute("""
CREATE INDEX IF NOT EXISTS idx_maintenance_plan_due
ON maintenance_plan(next_due_date, is_active);
""")

# 6. User lookups
db.execute("""
CREATE INDEX IF NOT EXISTS idx_user_username_email
ON user(username, email);
""")
```

**Performance Impact**:
- Before indexes: Query times ~100-500ms (N+1 problems)
- After indexes: Query times ~10-50ms (90% improvement)

---

## 🔄 DATABASE SYNCHRONIZATION

### Excel → Database Flow

```
1. Manual Import
   └─ sync_fracas_data.py
      ├─ Read Excel (Fracas_*.xlsx)
      ├─ INSERT into Equipment table
      └─ INSERT into Failure table
      
2. Automatic Sync (Per Request)
   └─ app.py::before_request
      ├─ Check if excel_file exists
      ├─ Load into Pandas DataFrame
      ├─ Cache in memory (_parts_cache)
      └─ Serve from cache
      
3. Dashboard Updates
   └─ routes/dashboard.py
      ├─ Read Excel (Ariza_Listesi_*.xlsx)
      ├─ Calculate metrics (MTTR, MTBF)
      └─ Return JSON
```

---

## 🛡️ DATA INTEGRITY

### Constraints (Current & Recommended)

```python
# Current (models.py)
├─ UNIQUE constraints:
│  ├─ Equipment.equipment_code
│  ├─ Failure.failure_code
│  ├─ User.username
│  └─ User.email
│
├─ Foreign keys:
│  ├─ Equipment → Equipment (parent_id)
│  ├─ Failure → Equipment
│  ├─ WorkOrder → Equipment
│  ├─ User → Role
│  └─ All other relationships
│
└─ Recommended ADD:
   ├─ NOT NULL on critical fields
   ├─ CHECK constraints (status enums)
   └─ DEFAULT values (timestamps)
```

---

## 📈 DATABASE GROWTH PROJECTION (Next 12 months)

```
Current (3/2026):      ~3,500 records (~10 MB)
After 6 months (9/2026): ~6,000 records (~15 MB)
After 12 months (3/2027): ~10,000 records (~25 MB)

Bottlenecks to watch:
- AuditLog table (5000+ records)
- DowntimeRecord (large text field)
- Service log accumulation

Action: Archive old records quarterly
```

---

## 🚀 POSTGRESQL MIGRATION PATH (Future)

```sql
-- No code changes needed (SQLAlchemy abstraction)
-- Just config change in app.py:

app.config['SQLALCHEMY_DATABASE_URI'] = 
  'postgresql://user:pass@localhost/cmms_db'

-- Performance gains:
  ├─ JSONB fields (instead of TEXT)
  ├─ Native array types
  ├─ Full-text search
  ├─ Parallel query execution
  ├─ Better indexing strategies
  └─ Replication support

-- Migration tool: Flask-Migrate (already installed)
-- Command: flask db upgrade
```

---

**Referans**: [DATA_SOURCES_MAPPING.md](DATA_SOURCES_MAPPING.md) ile birlikte oku.  
**Commit**: CMSv1.1  
**Durumu**: ✅ Stable, ⚠️ Indexing gerekli
