"""
CMMS Veritabanı Modelleri
Tunus Hafif Raylı Sistem için Kapsamlı Model Yapısı
EN 13306 Bakım Terminolojisi Standardına Uygun
"""

from datetime import datetime, date, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Kullanıcı modeli - Rol tabanlı erişim kontrolü"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')
    department = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    employee_id = db.Column(db.String(20))
    hourly_rate = db.Column(db.Float, default=0)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Beceri ve Uygunluk Yönetimi
    skills = db.Column(db.Text)  # JSON: ["elektrik", "mekanik", "hidrolik"]
    certifications = db.Column(db.Text)  # JSON: sertifikalar
    skill_level = db.Column(db.String(20), default='junior')  # junior, mid, senior, expert
    work_location = db.Column(db.String(100))  # Çalışma konumu
    shift_pattern = db.Column(db.String(50))  # Vardiya düzeni
    max_weekly_hours = db.Column(db.Integer, default=40)
    current_weekly_hours = db.Column(db.Float, default=0)
    is_available = db.Column(db.Boolean, default=True)
    availability_notes = db.Column(db.Text)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_role_display(self):
        roles = {
            'admin': 'Yönetici',
            'muhendis': 'Mühendis',
            'teknisyen': 'Teknisyen',
            'operator': 'Operatör',
            'user': 'Kullanıcı'
        }
        return roles.get(self.role, self.role)
    
    def get_skills_list(self):
        """Beceri listesini döndür"""
        if self.skills:
            try:
                return json.loads(self.skills)
            except:
                return []
        return []
    
    def has_skill(self, skill):
        """Belirli bir beceriye sahip mi kontrol et"""
        return skill.lower() in [s.lower() for s in self.get_skills_list()]
    
    def get_availability_status(self):
        """Uygunluk durumunu badge olarak döndür"""
        if not self.is_available:
            return ('danger', 'Müsait Değil')
        if self.current_weekly_hours >= self.max_weekly_hours:
            return ('warning', 'Doluluk')
        return ('success', 'Müsait')


class Equipment(db.Model):
    """Ekipman modeli - Tramvay ve alt sistem hiyerarşisi"""
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    equipment_type = db.Column(db.String(50))
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='aktif')
    criticality = db.Column(db.String(20), default='medium')
    
    installation_date = db.Column(db.DateTime)
    warranty_end_date = db.Column(db.DateTime)
    last_maintenance_date = db.Column(db.DateTime)
    
    total_km = db.Column(db.Float, default=0)
    total_hours = db.Column(db.Float, default=0)
    cycle_count = db.Column(db.Integer, default=0)
    
    # Aşınma Eşikleri ve Otomatik Bakım Tetikleme
    km_threshold = db.Column(db.Float, default=0)  # Bakım tetikleme km eşiği
    hours_threshold = db.Column(db.Float, default=0)  # Bakım tetikleme saat eşiği
    cycle_threshold = db.Column(db.Integer, default=0)  # Bakım tetikleme döngü eşiği
    wear_level = db.Column(db.Float, default=0)  # Aşınma seviyesi (0-100%)
    wear_threshold = db.Column(db.Float, default=80)  # Aşınma uyarı eşiği (%)
    last_km_at_maintenance = db.Column(db.Float, default=0)
    last_hours_at_maintenance = db.Column(db.Float, default=0)
    
    acquisition_cost = db.Column(db.Float, default=0)
    total_maintenance_cost = db.Column(db.Float, default=0)
    
    mtbf_hours = db.Column(db.Float, default=0)
    mttr_hours = db.Column(db.Float, default=0)
    availability_rate = db.Column(db.Float, default=100)
    reliability_rate = db.Column(db.Float, default=100)
    
    total_downtime_planned = db.Column(db.Integer, default=0)
    total_downtime_unplanned = db.Column(db.Integer, default=0)
    
    # Hiyerarşik Kodlama (Tren > Alt Sistem > Parça)
    hierarchy_level = db.Column(db.Integer, default=1)  # 1: Tren, 2: Alt Sistem, 3: Parça
    hierarchy_path = db.Column(db.String(200))  # Örn: "TRN-001/SYS-FREN/PRT-DISK"
    
    # Gerekli Beceriler
    required_skills = db.Column(db.Text)  # JSON: bakım için gerekli beceriler
    
    parent_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=True)
    notes = db.Column(db.Text)
    technical_specs = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    children = db.relationship('Equipment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    failures = db.relationship('Failure', backref='equipment', lazy='dynamic')
    work_orders = db.relationship('WorkOrder', backref='equipment', lazy='dynamic')
    maintenance_plans = db.relationship('MaintenancePlan', backref='equipment', lazy='dynamic')
    downtimes = db.relationship('DowntimeRecord', backref='equipment', lazy='dynamic')
    meter_readings = db.relationship('MeterReading', backref='equipment', lazy='dynamic')
    documents = db.relationship('TechnicalDocument', backref='equipment', lazy='dynamic')
    
    def get_status_badge(self):
        badges = {
            'aktif': ('success', 'Aktif'),
            'bakim': ('warning', 'Bakımda'),
            'ariza': ('danger', 'Arızalı'),
            'depo': ('secondary', 'Depoda')
        }
        return badges.get(self.status, ('secondary', self.status))
    
    def get_criticality_badge(self):
        badges = {
            'critical': ('danger', 'Kritik'),
            'high': ('warning', 'Yüksek'),
            'medium': ('info', 'Orta'),
            'low': ('secondary', 'Düşük')
        }
        return badges.get(self.criticality, ('secondary', self.criticality))
    
    def calculate_availability(self, days=30):
        start_date = datetime.now() - timedelta(days=days)
        total_minutes = days * 24 * 60
        downtimes = DowntimeRecord.query.filter(
            DowntimeRecord.equipment_id == self.id,
            DowntimeRecord.start_time >= start_date
        ).all()
        downtime_minutes = sum(d.duration_minutes or 0 for d in downtimes)
        availability = ((total_minutes - downtime_minutes) / total_minutes) * 100
        return round(availability, 2)
    
    def calculate_mtbf(self):
        failures = Failure.query.filter_by(equipment_id=self.id).order_by(Failure.created_at).all()
        if len(failures) < 2:
            return 0
        total_time = 0
        for i in range(1, len(failures)):
            diff = failures[i].created_at - failures[i-1].created_at
            total_time += diff.total_seconds() / 3600
        return round(total_time / (len(failures) - 1), 2)
    
    def calculate_mttr(self):
        failures = Failure.query.filter(
            Failure.equipment_id == self.id,
            Failure.resolved_date != None
        ).all()
        if not failures:
            return 0
        total_repair_time = sum(f.downtime_minutes or 0 for f in failures)
        return round(total_repair_time / len(failures) / 60, 2)
    
    def get_health_score(self):
        score = 100
        if self.failures.filter_by(status='acik').count() > 0:
            score -= 30
        if self.failures.filter_by(status='devam_ediyor').count() > 0:
            score -= 15
        overdue_plans = MaintenancePlan.query.filter(
            MaintenancePlan.equipment_id == self.id,
            MaintenancePlan.next_due_date < date.today(),
            MaintenancePlan.is_active == True
        ).count()
        if overdue_plans > 0:
            score -= 20
        if self.availability_rate < 90:
            score -= 15
        elif self.availability_rate < 95:
            score -= 5
        return max(0, score)
    
    def get_health_badge(self):
        score = self.get_health_score()
        if score >= 80:
            return ('success', 'İyi')
        elif score >= 60:
            return ('warning', 'Orta')
        else:
            return ('danger', 'Kritik')


class Failure(db.Model):
    """Arıza kayıtları modeli"""
    __tablename__ = 'failures'
    
    id = db.Column(db.Integer, primary_key=True)
    failure_code = db.Column(db.String(50), unique=True, nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    
    severity = db.Column(db.String(20))
    failure_type = db.Column(db.String(50))
    failure_mode = db.Column(db.String(100))
    root_cause = db.Column(db.String(200))
    
    status = db.Column(db.String(20), default='acik')
    
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    failure_date = db.Column(db.DateTime, default=datetime.utcnow)
    detected_date = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_date = db.Column(db.DateTime)
    
    downtime_minutes = db.Column(db.Integer, default=0)
    repair_cost = db.Column(db.Float, default=0)
    impact_description = db.Column(db.Text)
    
    resolution_notes = db.Column(db.Text)
    corrective_action = db.Column(db.Text)
    preventive_action = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    reporter = db.relationship('User', foreign_keys=[reported_by], backref='reported_failures')
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_failures')
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='resolved_failures')
    
    def get_severity_badge(self):
        badges = {
            'kritik': ('danger', 'Kritik'),
            'yuksek': ('warning', 'Yüksek'),
            'orta': ('info', 'Orta'),
            'dusuk': ('secondary', 'Düşük')
        }
        return badges.get(self.severity, ('secondary', self.severity))
    
    def get_status_badge(self):
        badges = {
            'acik': ('danger', 'Açık'),
            'devam_ediyor': ('warning', 'Devam Ediyor'),
            'cozuldu': ('success', 'Çözüldü')
        }
        return badges.get(self.status, ('secondary', self.status))
    
    def get_response_time(self):
        if self.resolved_date and self.created_at:
            diff = self.resolved_date - self.created_at
            return int(diff.total_seconds() / 60)
        return None


class WorkOrder(db.Model):
    """İş emri modeli"""
    __tablename__ = 'work_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_code = db.Column(db.String(50), unique=True, nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    failure_id = db.Column(db.Integer, db.ForeignKey('failures.id'), nullable=True)
    maintenance_plan_id = db.Column(db.Integer, db.ForeignKey('maintenance_plans.id'), nullable=True)
    
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    work_type = db.Column(db.String(50))
    priority = db.Column(db.String(20), default='normal')
    status = db.Column(db.String(20), default='beklemede')
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    planned_start = db.Column(db.DateTime)
    planned_end = db.Column(db.DateTime)
    actual_start = db.Column(db.DateTime)
    actual_end = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    
    work_instructions = db.Column(db.Text)
    safety_notes = db.Column(db.Text)
    completion_notes = db.Column(db.Text)
    
    labor_hours = db.Column(db.Float, default=0)
    labor_cost = db.Column(db.Float, default=0)
    material_cost = db.Column(db.Float, default=0)
    external_cost = db.Column(db.Float, default=0)
    total_cost = db.Column(db.Float, default=0)
    
    downtime_minutes = db.Column(db.Integer, default=0)
    
    checklist = db.Column(db.Text)
    checklist_completed = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_orders')
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_orders')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_orders')
    failure = db.relationship('Failure', backref='work_orders')
    parts_used = db.relationship('WorkOrderPart', backref='work_order', lazy='dynamic')
    
    def get_priority_badge(self):
        badges = {
            'acil': ('danger', 'Acil'),
            'yuksek': ('warning', 'Yüksek'),
            'normal': ('info', 'Normal'),
            'dusuk': ('secondary', 'Düşük')
        }
        return badges.get(self.priority, ('secondary', self.priority))
    
    def get_status_badge(self):
        badges = {
            'beklemede': ('secondary', 'Beklemede'),
            'onay_bekliyor': ('info', 'Onay Bekliyor'),
            'devam_ediyor': ('primary', 'Devam Ediyor'),
            'tamamlandi': ('success', 'Tamamlandı'),
            'iptal': ('dark', 'İptal')
        }
        return badges.get(self.status, ('secondary', self.status))
    
    def get_work_type_display(self):
        types = {
            'ariza_onarim': 'Arıza Onarım',
            'periyodik_bakim': 'Periyodik Bakım',
            'koruyucu_bakim': 'Koruyucu Bakım',
            'revizyon': 'Revizyon',
            'muayene': 'Muayene/Kontrol'
        }
        return types.get(self.work_type, self.work_type)
    
    def calculate_total_cost(self):
        parts_cost = sum(p.total_price for p in self.parts_used.all())
        self.total_cost = self.labor_cost + self.material_cost + self.external_cost + parts_cost
        return self.total_cost
    
    def is_overdue(self):
        if self.status in ['tamamlandi', 'iptal']:
            return False
        if self.planned_end and datetime.now() > self.planned_end:
            return True
        return False


class WorkOrderPart(db.Model):
    """İş emrinde kullanılan parçalar"""
    __tablename__ = 'work_order_parts'
    
    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'))
    spare_part_id = db.Column(db.Integer, db.ForeignKey('spare_parts.id'))
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, default=0)
    total_price = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    spare_part = db.relationship('SparePartInventory', backref='usage_records')


class MaintenancePlan(db.Model):
    """Bakım planı modeli"""
    __tablename__ = 'maintenance_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_code = db.Column(db.String(50), unique=True, nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    name = db.Column(db.String(200))
    description = db.Column(db.Text)
    
    maintenance_type = db.Column(db.String(50))
    maintenance_category = db.Column(db.String(50))
    
    frequency_days = db.Column(db.Integer)
    frequency_km = db.Column(db.Integer, nullable=True)
    frequency_hours = db.Column(db.Integer, nullable=True)
    
    last_performed_date = db.Column(db.Date)
    next_due_date = db.Column(db.Date)
    
    estimated_duration = db.Column(db.Integer)
    estimated_cost = db.Column(db.Float, default=0)
    work_instructions = db.Column(db.Text)
    safety_requirements = db.Column(db.Text)
    required_skills = db.Column(db.String(200))
    required_parts = db.Column(db.Text)
    checklist = db.Column(db.Text)
    
    auto_generate_wo = db.Column(db.Boolean, default=True)
    advance_notice_days = db.Column(db.Integer, default=7)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    work_orders = db.relationship('WorkOrder', backref='maintenance_plan', lazy='dynamic')
    
    def is_overdue(self):
        if self.next_due_date:
            return self.next_due_date < date.today()
        return False
    
    def days_until_due(self):
        if self.next_due_date:
            delta = self.next_due_date - date.today()
            return delta.days
        return None
    
    def get_status(self):
        if not self.is_active:
            return ('secondary', 'Pasif')
        if self.is_overdue():
            return ('danger', 'Gecikmiş')
        days = self.days_until_due()
        if days is not None and days <= 7:
            return ('warning', 'Yaklaşıyor')
        return ('success', 'Planlandı')


class SparePartInventory(db.Model):
    """Yedek parça envanter modeli"""
    __tablename__ = 'spare_parts'
    
    id = db.Column(db.Integer, primary_key=True)
    part_code = db.Column(db.String(50), unique=True, nullable=False)
    part_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    
    current_quantity = db.Column(db.Integer, default=0)
    min_quantity = db.Column(db.Integer, default=5)
    max_quantity = db.Column(db.Integer, default=100)
    reorder_quantity = db.Column(db.Integer, default=20)
    
    unit_price = db.Column(db.Float, default=0)
    last_purchase_price = db.Column(db.Float, default=0)
    average_price = db.Column(db.Float, default=0)
    
    supplier = db.Column(db.String(100))
    supplier_part_number = db.Column(db.String(100))
    lead_time_days = db.Column(db.Integer, default=14)
    
    location = db.Column(db.String(100))
    shelf_number = db.Column(db.String(50))
    
    compatible_equipment = db.Column(db.Text)
    
    last_purchase_date = db.Column(db.DateTime)
    last_used_date = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    transactions = db.relationship('StockTransaction', backref='spare_part', lazy='dynamic')
    
    def is_low_stock(self):
        return self.current_quantity <= self.min_quantity
    
    def get_stock_status(self):
        if self.current_quantity == 0:
            return ('danger', 'Stok Yok')
        elif self.current_quantity <= self.min_quantity:
            return ('warning', 'Kritik')
        elif self.current_quantity >= self.max_quantity:
            return ('info', 'Fazla Stok')
        else:
            return ('success', 'Yeterli')
    
    def get_stock_value(self):
        return self.current_quantity * self.unit_price


class StockTransaction(db.Model):
    """Stok hareketleri"""
    __tablename__ = 'stock_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    spare_part_id = db.Column(db.Integer, db.ForeignKey('spare_parts.id'))
    transaction_type = db.Column(db.String(20))
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Float, default=0)
    reference_type = db.Column(db.String(50))
    reference_id = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='stock_transactions')


class DowntimeRecord(db.Model):
    """Duruş kayıtları"""
    __tablename__ = 'downtime_records'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    failure_id = db.Column(db.Integer, db.ForeignKey('failures.id'), nullable=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=True)
    
    downtime_type = db.Column(db.String(50))
    reason = db.Column(db.String(200))
    description = db.Column(db.Text)
    
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    
    impact = db.Column(db.String(50))
    service_affected = db.Column(db.Boolean, default=False)
    passenger_impact = db.Column(db.Integer, default=0)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='downtime_records')
    failure = db.relationship('Failure', backref='downtime_records')
    work_order = db.relationship('WorkOrder', backref='downtime_records')
    
    def calculate_duration(self):
        if self.start_time and self.end_time:
            diff = self.end_time - self.start_time
            self.duration_minutes = int(diff.total_seconds() / 60)
        return self.duration_minutes


class MeterReading(db.Model):
    """Sayaç okumaları"""
    __tablename__ = 'meter_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    meter_type = db.Column(db.String(50))
    reading_value = db.Column(db.Float)
    reading_date = db.Column(db.DateTime, default=datetime.utcnow)
    previous_reading = db.Column(db.Float)
    delta_value = db.Column(db.Float)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    
    user = db.relationship('User', backref='meter_readings')


class KPISnapshot(db.Model):
    """KPI anlık görüntüleri"""
    __tablename__ = 'kpi_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    snapshot_date = db.Column(db.Date, default=date.today)
    period_type = db.Column(db.String(20))
    
    total_fleet = db.Column(db.Integer, default=0)
    active_fleet = db.Column(db.Integer, default=0)
    fleet_availability = db.Column(db.Float, default=0)
    
    total_failures = db.Column(db.Integer, default=0)
    resolved_failures = db.Column(db.Integer, default=0)
    critical_failures = db.Column(db.Integer, default=0)
    avg_resolution_time = db.Column(db.Float, default=0)
    
    total_work_orders = db.Column(db.Integer, default=0)
    completed_work_orders = db.Column(db.Integer, default=0)
    overdue_work_orders = db.Column(db.Integer, default=0)
    on_time_completion_rate = db.Column(db.Float, default=0)
    
    planned_maintenance = db.Column(db.Integer, default=0)
    unplanned_maintenance = db.Column(db.Integer, default=0)
    preventive_ratio = db.Column(db.Float, default=0)
    
    total_downtime_minutes = db.Column(db.Integer, default=0)
    planned_downtime_minutes = db.Column(db.Integer, default=0)
    unplanned_downtime_minutes = db.Column(db.Integer, default=0)
    
    total_maintenance_cost = db.Column(db.Float, default=0)
    labor_cost = db.Column(db.Float, default=0)
    material_cost = db.Column(db.Float, default=0)
    
    fleet_mtbf = db.Column(db.Float, default=0)
    fleet_mttr = db.Column(db.Float, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SystemAlert(db.Model):
    """Sistem uyarıları"""
    __tablename__ = 'system_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(50))
    severity = db.Column(db.String(20))
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    
    reference_type = db.Column(db.String(50))
    reference_id = db.Column(db.Integer)
    
    is_read = db.Column(db.Boolean, default=False)
    is_dismissed = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    read_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def get_severity_badge(self):
        badges = {
            'critical': ('danger', 'Kritik'),
            'warning': ('warning', 'Uyarı'),
            'info': ('info', 'Bilgi')
        }
        return badges.get(self.severity, ('secondary', self.severity))


# ==================== ISO 55000 VARLIK YÖNETİMİ MODELLERİ ====================

class ResourceAllocation(db.Model):
    """İnsan kaynakları tahsisi - ISO 55000 Uyumlu"""
    __tablename__ = 'resource_allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    role_type = db.Column(db.String(50))  # lead, technician, helper, supervisor
    skill_required = db.Column(db.String(100))
    
    planned_hours = db.Column(db.Float, default=0)
    actual_hours = db.Column(db.Float, default=0)
    overtime_hours = db.Column(db.Float, default=0)
    
    hourly_rate = db.Column(db.Float, default=0)
    total_cost = db.Column(db.Float, default=0)
    
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    
    status = db.Column(db.String(20), default='planned')  # planned, in_progress, completed
    performance_rating = db.Column(db.Integer)  # 1-5
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='resource_allocations')
    work_order = db.relationship('WorkOrder', backref='resource_allocations')
    
    def calculate_cost(self):
        total_hours = self.actual_hours + (self.overtime_hours * 1.5)
        self.total_cost = total_hours * self.hourly_rate
        return self.total_cost


class MaterialConsumption(db.Model):
    """Malzeme tüketimi takibi - ISO 55000 Uyumlu"""
    __tablename__ = 'material_consumptions'
    
    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'))
    spare_part_id = db.Column(db.Integer, db.ForeignKey('spare_parts.id'))
    
    planned_quantity = db.Column(db.Integer, default=0)
    actual_quantity = db.Column(db.Integer, default=0)
    waste_quantity = db.Column(db.Integer, default=0)
    
    unit_cost = db.Column(db.Float, default=0)
    total_cost = db.Column(db.Float, default=0)
    
    reason = db.Column(db.String(200))
    batch_number = db.Column(db.String(50))
    
    consumed_at = db.Column(db.DateTime, default=datetime.utcnow)
    consumed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    work_order = db.relationship('WorkOrder', backref='material_consumptions')
    spare_part = db.relationship('SparePartInventory', backref='consumptions')
    user = db.relationship('User', backref='material_consumptions')


class CostCenter(db.Model):
    """Maliyet merkezi - Finansal kaynak yönetimi"""
    __tablename__ = 'cost_centers'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    budget_annual = db.Column(db.Float, default=0)
    budget_monthly = db.Column(db.Float, default=0)
    spent_ytd = db.Column(db.Float, default=0)
    spent_mtd = db.Column(db.Float, default=0)
    
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('cost_centers.id'))
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    manager = db.relationship('User', backref='managed_cost_centers')
    children = db.relationship('CostCenter', backref=db.backref('parent', remote_side=[id]))
    
    def get_remaining_budget(self):
        return self.budget_annual - self.spent_ytd
    
    def get_budget_utilization(self):
        if self.budget_annual > 0:
            return (self.spent_ytd / self.budget_annual) * 100
        return 0


class MaintenanceBudget(db.Model):
    """Bakım bütçesi takibi"""
    __tablename__ = 'maintenance_budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    cost_center_id = db.Column(db.Integer, db.ForeignKey('cost_centers.id'))
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=True)
    
    budget_labor = db.Column(db.Float, default=0)
    budget_material = db.Column(db.Float, default=0)
    budget_external = db.Column(db.Float, default=0)
    budget_total = db.Column(db.Float, default=0)
    
    actual_labor = db.Column(db.Float, default=0)
    actual_material = db.Column(db.Float, default=0)
    actual_external = db.Column(db.Float, default=0)
    actual_total = db.Column(db.Float, default=0)
    
    variance = db.Column(db.Float, default=0)
    variance_percentage = db.Column(db.Float, default=0)
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    cost_center = db.relationship('CostCenter', backref='budgets')
    equipment = db.relationship('Equipment', backref='budgets')
    
    def calculate_variance(self):
        self.actual_total = self.actual_labor + self.actual_material + self.actual_external
        self.variance = self.budget_total - self.actual_total
        if self.budget_total > 0:
            self.variance_percentage = (self.variance / self.budget_total) * 100


# ==================== TAHMİNE DAYALI ANALİZ MODELLERİ ====================

class SensorData(db.Model):
    """Trenlerden toplanan sensör verileri - Gerçek zamanlı izleme"""
    __tablename__ = 'sensor_data'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    sensor_type = db.Column(db.String(50))  # temperature, vibration, pressure, speed, current
    sensor_location = db.Column(db.String(100))
    
    value = db.Column(db.Float)
    unit = db.Column(db.String(20))
    
    min_threshold = db.Column(db.Float)
    max_threshold = db.Column(db.Float)
    is_alarm = db.Column(db.Boolean, default=False)
    alarm_level = db.Column(db.String(20))  # warning, critical
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    equipment = db.relationship('Equipment', backref='sensor_readings')
    
    def check_threshold(self):
        if self.max_threshold and self.value > self.max_threshold:
            self.is_alarm = True
            self.alarm_level = 'critical' if self.value > self.max_threshold * 1.2 else 'warning'
        elif self.min_threshold and self.value < self.min_threshold:
            self.is_alarm = True
            self.alarm_level = 'critical' if self.value < self.min_threshold * 0.8 else 'warning'
        else:
            self.is_alarm = False
            self.alarm_level = None
        return self.is_alarm


class PredictiveModel(db.Model):
    """Tahmine dayalı bakım modelleri"""
    __tablename__ = 'predictive_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    equipment_type = db.Column(db.String(50))
    component = db.Column(db.String(100))
    
    model_type = db.Column(db.String(50))  # regression, classification, time_series
    algorithm = db.Column(db.String(50))  # random_forest, gradient_boost, lstm
    
    input_features = db.Column(db.Text)  # JSON list of features
    target_variable = db.Column(db.String(100))
    
    accuracy = db.Column(db.Float, default=0)
    precision = db.Column(db.Float, default=0)
    recall = db.Column(db.Float, default=0)
    f1_score = db.Column(db.Float, default=0)
    
    training_date = db.Column(db.DateTime)
    last_prediction_date = db.Column(db.DateTime)
    version = db.Column(db.String(20))
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FailurePrediction(db.Model):
    """Arıza tahminleri"""
    __tablename__ = 'failure_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    model_id = db.Column(db.Integer, db.ForeignKey('predictive_models.id'))
    
    predicted_failure_type = db.Column(db.String(100))
    predicted_component = db.Column(db.String(100))
    
    probability = db.Column(db.Float)  # 0-100
    confidence_level = db.Column(db.String(20))  # low, medium, high
    
    predicted_date = db.Column(db.Date)
    days_until_failure = db.Column(db.Integer)
    
    risk_level = db.Column(db.String(20))  # low, medium, high, critical
    recommended_action = db.Column(db.Text)
    
    is_validated = db.Column(db.Boolean, default=False)
    actual_failure_id = db.Column(db.Integer, db.ForeignKey('failures.id'), nullable=True)
    validation_accuracy = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    equipment = db.relationship('Equipment', backref='failure_predictions')
    model = db.relationship('PredictiveModel', backref='predictions')
    actual_failure = db.relationship('Failure', backref='predictions')
    
    def get_risk_badge(self):
        badges = {
            'critical': ('danger', 'Kritik'),
            'high': ('warning', 'Yüksek'),
            'medium': ('info', 'Orta'),
            'low': ('secondary', 'Düşük')
        }
        return badges.get(self.risk_level, ('secondary', self.risk_level))


class ComponentHealthIndex(db.Model):
    """Bileşen sağlık endeksi - Tahmine dayalı analiz"""
    __tablename__ = 'component_health_index'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    component_name = db.Column(db.String(100))
    
    health_index = db.Column(db.Float, default=100)  # 0-100
    degradation_rate = db.Column(db.Float, default=0)  # % per month
    
    remaining_useful_life = db.Column(db.Integer)  # days
    confidence_interval = db.Column(db.Float)  # %
    
    last_assessment_date = db.Column(db.DateTime)
    next_assessment_date = db.Column(db.DateTime)
    
    factors = db.Column(db.Text)  # JSON: factors affecting health
    trend = db.Column(db.String(20))  # improving, stable, degrading
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    equipment = db.relationship('Equipment', backref='health_indices')
    
    def get_health_badge(self):
        if self.health_index >= 80:
            return ('success', 'İyi')
        elif self.health_index >= 60:
            return ('warning', 'Dikkat')
        elif self.health_index >= 40:
            return ('orange', 'Riskli')
        else:
            return ('danger', 'Kritik')


# ==================== EN 15341 BAKIM PERFORMANS GÖSTERGELERİ ====================

class EN15341_KPI(db.Model):
    """EN 15341 Bakım performans göstergeleri"""
    __tablename__ = 'en15341_kpi'
    
    id = db.Column(db.Integer, primary_key=True)
    snapshot_date = db.Column(db.Date, default=date.today)
    period_type = db.Column(db.String(20))  # daily, weekly, monthly, yearly
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=True)
    
    # Ekonomik göstergeler (E1-E24)
    e1_total_maintenance_cost = db.Column(db.Float, default=0)  # Toplam bakım maliyeti
    e2_maintenance_cost_per_unit = db.Column(db.Float, default=0)  # Birim bakım maliyeti
    e3_preventive_cost_ratio = db.Column(db.Float, default=0)  # Önleyici bakım maliyet oranı
    e4_corrective_cost_ratio = db.Column(db.Float, default=0)  # Düzeltici bakım maliyet oranı
    e5_labor_cost_ratio = db.Column(db.Float, default=0)  # İşçilik maliyet oranı
    e6_material_cost_ratio = db.Column(db.Float, default=0)  # Malzeme maliyet oranı
    e7_external_cost_ratio = db.Column(db.Float, default=0)  # Dış kaynak maliyet oranı
    e8_maintenance_cost_per_output = db.Column(db.Float, default=0)  # Üretim birimi başına bakım maliyeti
    
    # Teknik göstergeler (T1-T21)
    t1_availability = db.Column(db.Float, default=0)  # Kullanılabilirlik
    t2_mtbf = db.Column(db.Float, default=0)  # Ortalama arızalar arası süre
    t3_mttr = db.Column(db.Float, default=0)  # Ortalama onarım süresi
    t4_mttf = db.Column(db.Float, default=0)  # Ortalama arızaya kadar süre
    t5_failure_rate = db.Column(db.Float, default=0)  # Arıza oranı
    t6_preventive_ratio = db.Column(db.Float, default=0)  # Önleyici bakım oranı
    t7_planned_ratio = db.Column(db.Float, default=0)  # Planlı bakım oranı
    t8_schedule_compliance = db.Column(db.Float, default=0)  # Program uyumu
    t9_emergency_ratio = db.Column(db.Float, default=0)  # Acil bakım oranı
    t10_rework_ratio = db.Column(db.Float, default=0)  # Yeniden işlem oranı
    
    # Organizasyonel göstergeler (O1-O14)
    o1_maintenance_productivity = db.Column(db.Float, default=0)  # Bakım verimliliği
    o2_training_hours = db.Column(db.Float, default=0)  # Eğitim saatleri
    o3_overtime_ratio = db.Column(db.Float, default=0)  # Fazla mesai oranı
    o4_absenteeism_rate = db.Column(db.Float, default=0)  # Devamsızlık oranı
    o5_wo_completion_rate = db.Column(db.Float, default=0)  # İş emri tamamlama oranı
    o6_wo_on_time_rate = db.Column(db.Float, default=0)  # Zamanında tamamlama oranı
    o7_backlog_hours = db.Column(db.Float, default=0)  # Bekleyen iş saatleri
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    equipment = db.relationship('Equipment', backref='en15341_kpis')


# ==================== ISO 27001 SİBER GÜVENLİK MODELLERİ ====================

class AuditLog(db.Model):
    """Denetim günlüğü - ISO 27001 uyumlu tam izlenebilirlik"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    action = db.Column(db.String(50))  # create, update, delete, view, login, logout, export
    entity_type = db.Column(db.String(50))  # equipment, failure, work_order, etc.
    entity_id = db.Column(db.Integer)
    entity_code = db.Column(db.String(50))
    
    old_values = db.Column(db.Text)  # JSON
    new_values = db.Column(db.Text)  # JSON
    changes = db.Column(db.Text)  # JSON summary of changes
    
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    session_id = db.Column(db.String(100))
    
    status = db.Column(db.String(20), default='success')  # success, failed, blocked
    error_message = db.Column(db.Text)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='audit_logs')


class DataAccessLog(db.Model):
    """Veri erişim günlüğü - ISO 27001 uyumlu"""
    __tablename__ = 'data_access_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    access_type = db.Column(db.String(50))  # read, write, export, print
    data_category = db.Column(db.String(50))  # sensitive, confidential, public
    resource = db.Column(db.String(100))
    
    query_details = db.Column(db.Text)
    records_accessed = db.Column(db.Integer, default=0)
    
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='data_access_logs')


class SecurityIncident(db.Model):
    """Güvenlik olayları - ISO 27001"""
    __tablename__ = 'security_incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_code = db.Column(db.String(50), unique=True)
    
    incident_type = db.Column(db.String(50))  # unauthorized_access, data_breach, malware, etc.
    severity = db.Column(db.String(20))  # low, medium, high, critical
    
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    
    affected_systems = db.Column(db.Text)
    affected_data = db.Column(db.Text)
    
    detected_at = db.Column(db.DateTime)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    status = db.Column(db.String(20), default='open')  # open, investigating, resolved, closed
    
    root_cause = db.Column(db.Text)
    corrective_actions = db.Column(db.Text)
    preventive_actions = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reporter = db.relationship('User', foreign_keys=[reported_by], backref='reported_incidents')
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_incidents')


class UserSession(db.Model):
    """Kullanıcı oturum takibi - ISO 27001"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    session_id = db.Column(db.String(100), unique=True)
    
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    logout_time = db.Column(db.DateTime)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    device_type = db.Column(db.String(50))
    
    is_active = db.Column(db.Boolean, default=True)
    terminated_reason = db.Column(db.String(100))  # logout, timeout, forced, security
    
    user = db.relationship('User', backref='sessions')


class PasswordHistory(db.Model):
    """Şifre geçmişi - ISO 27001"""
    __tablename__ = 'password_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    password_hash = db.Column(db.String(255))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='password_history')


# ==================== MODÜLER MİMARİ - ENTEGRASYON MODELLERİ ====================

class IntegrationConfig(db.Model):
    """Entegrasyon konfigürasyonları - Modüler mimari"""
    __tablename__ = 'integration_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    integration_type = db.Column(db.String(50))  # api, database, file, mqtt, opc_ua
    
    endpoint_url = db.Column(db.String(255))
    authentication_type = db.Column(db.String(50))  # none, basic, token, oauth2, certificate
    credentials = db.Column(db.Text)  # Encrypted JSON
    
    data_format = db.Column(db.String(20))  # json, xml, csv
    sync_frequency = db.Column(db.Integer)  # minutes
    last_sync = db.Column(db.DateTime)
    next_sync = db.Column(db.DateTime)
    
    status = db.Column(db.String(20), default='inactive')  # active, inactive, error
    error_message = db.Column(db.Text)
    
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class IntegrationLog(db.Model):
    """Entegrasyon günlükleri"""
    __tablename__ = 'integration_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey('integration_configs.id'))
    
    direction = db.Column(db.String(20))  # inbound, outbound
    operation = db.Column(db.String(50))
    
    records_processed = db.Column(db.Integer, default=0)
    records_success = db.Column(db.Integer, default=0)
    records_failed = db.Column(db.Integer, default=0)
    
    request_data = db.Column(db.Text)
    response_data = db.Column(db.Text)
    
    status = db.Column(db.String(20))  # success, partial, failed
    error_message = db.Column(db.Text)
    
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    duration_ms = db.Column(db.Integer)
    
    config = db.relationship('IntegrationConfig', backref='logs')


class ModuleRegistry(db.Model):
    """Modül kaydı - Ölçeklenebilir platform"""
    __tablename__ = 'module_registry'
    
    id = db.Column(db.Integer, primary_key=True)
    module_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20))
    
    description = db.Column(db.Text)
    dependencies = db.Column(db.Text)  # JSON list of module codes
    
    api_endpoints = db.Column(db.Text)  # JSON list of endpoints
    permissions_required = db.Column(db.Text)  # JSON list of permissions
    
    status = db.Column(db.String(20), default='inactive')  # active, inactive, maintenance
    installed_at = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)
    
    is_core = db.Column(db.Boolean, default=False)
    is_licensed = db.Column(db.Boolean, default=True)
    license_expiry = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==================== TEKNİK DOKÜMANTASYON YÖNETİMİ ====================

class TechnicalDocument(db.Model):
    """Teknik dokümanlar - Planlar, kılavuzlar, şemalar"""
    __tablename__ = 'technical_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    document_code = db.Column(db.String(50), unique=True, nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=True)
    
    title = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(50))  # manual, schematic, procedure, datasheet, certificate
    category = db.Column(db.String(50))  # electrical, mechanical, hydraulic, software
    
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    file_name = db.Column(db.String(200))
    file_type = db.Column(db.String(20))  # pdf, dwg, doc, xls
    file_size = db.Column(db.Integer)  # bytes
    
    version = db.Column(db.String(20), default='1.0')
    revision_date = db.Column(db.DateTime)
    revision_notes = db.Column(db.Text)
    
    language = db.Column(db.String(10), default='tr')  # tr, en, fr, ar
    
    # Erişim kontrolü
    access_level = db.Column(db.String(20), default='public')  # public, restricted, confidential
    allowed_roles = db.Column(db.Text)  # JSON: ["admin", "muhendis"]
    
    # Meta veriler
    author = db.Column(db.String(100))
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approval_date = db.Column(db.DateTime)
    
    tags = db.Column(db.Text)  # JSON: etiketler
    
    view_count = db.Column(db.Integer, default=0)
    download_count = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    approver = db.relationship('User', backref='approved_documents')
    
    def get_type_badge(self):
        badges = {
            'manual': ('primary', 'Kılavuz'),
            'schematic': ('info', 'Şema'),
            'procedure': ('success', 'Prosedür'),
            'datasheet': ('secondary', 'Veri Sayfası'),
            'certificate': ('warning', 'Sertifika')
        }
        return badges.get(self.document_type, ('secondary', self.document_type))
    
    def get_file_icon(self):
        icons = {
            'pdf': 'bi-file-pdf text-danger',
            'doc': 'bi-file-word text-primary',
            'docx': 'bi-file-word text-primary',
            'xls': 'bi-file-excel text-success',
            'xlsx': 'bi-file-excel text-success',
            'dwg': 'bi-file-earmark text-warning',
            'jpg': 'bi-file-image text-info',
            'png': 'bi-file-image text-info'
        }
        return icons.get(self.file_type, 'bi-file-earmark')


class DocumentRevision(db.Model):
    """Doküman revizyon geçmişi"""
    __tablename__ = 'document_revisions'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('technical_documents.id'))
    
    version = db.Column(db.String(20))
    revision_date = db.Column(db.DateTime, default=datetime.utcnow)
    revision_notes = db.Column(db.Text)
    
    file_path = db.Column(db.String(500))
    revised_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    document = db.relationship('TechnicalDocument', backref='revisions')
    user = db.relationship('User', backref='document_revisions')


# ==================== OTOMATİK BAKIM TETİKLEME ====================

class MaintenanceTrigger(db.Model):
    """Otomatik bakım tetikleyicileri"""
    __tablename__ = 'maintenance_triggers'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    maintenance_plan_id = db.Column(db.Integer, db.ForeignKey('maintenance_plans.id'))
    
    trigger_type = db.Column(db.String(50))  # km, hours, cycles, date, condition, sensor
    trigger_name = db.Column(db.String(100))
    
    # Eşik değerleri
    threshold_value = db.Column(db.Float)
    current_value = db.Column(db.Float, default=0)
    threshold_unit = db.Column(db.String(20))  # km, saat, döngü, gün
    
    # Koşul bazlı tetikleme
    condition_type = db.Column(db.String(50))  # sensor_value, wear_level, temperature
    condition_operator = db.Column(db.String(10))  # >, <, >=, <=, ==
    condition_value = db.Column(db.Float)
    
    # Durum
    is_active = db.Column(db.Boolean, default=True)
    is_triggered = db.Column(db.Boolean, default=False)
    last_triggered = db.Column(db.DateTime)
    trigger_count = db.Column(db.Integer, default=0)
    
    # Otomatik iş emri oluşturma
    auto_create_wo = db.Column(db.Boolean, default=True)
    wo_priority = db.Column(db.String(20), default='normal')
    advance_warning_value = db.Column(db.Float)  # Ön uyarı değeri
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    equipment = db.relationship('Equipment', backref='maintenance_triggers')
    maintenance_plan = db.relationship('MaintenancePlan', backref='triggers')
    
    def check_trigger(self):
        """Tetikleme koşulunu kontrol et"""
        if self.trigger_type == 'km':
            if self.equipment and self.equipment.total_km:
                km_since_last = self.equipment.total_km - self.equipment.last_km_at_maintenance
                self.current_value = km_since_last
                return km_since_last >= self.threshold_value
        elif self.trigger_type == 'hours':
            if self.equipment and self.equipment.total_hours:
                hours_since_last = self.equipment.total_hours - self.equipment.last_hours_at_maintenance
                self.current_value = hours_since_last
                return hours_since_last >= self.threshold_value
        elif self.trigger_type == 'condition':
            if self.equipment and self.equipment.wear_level:
                self.current_value = self.equipment.wear_level
                if self.condition_operator == '>=':
                    return self.equipment.wear_level >= self.condition_value
                elif self.condition_operator == '>':
                    return self.equipment.wear_level > self.condition_value
        return False
    
    def get_progress_percentage(self):
        """Eşiğe olan ilerleme yüzdesini hesapla"""
        if self.threshold_value and self.threshold_value > 0:
            return min((self.current_value / self.threshold_value) * 100, 100)
        return 0


class MaintenanceAlert(db.Model):
    """Bakım uyarıları - Otomatik bildirimler"""
    __tablename__ = 'maintenance_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    trigger_id = db.Column(db.Integer, db.ForeignKey('maintenance_triggers.id'), nullable=True)
    
    alert_type = db.Column(db.String(50))  # threshold_warning, threshold_reached, anomaly, prediction
    severity = db.Column(db.String(20))  # info, warning, critical
    
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    
    # İlgili veriler
    metric_name = db.Column(db.String(50))
    metric_value = db.Column(db.Float)
    threshold_value = db.Column(db.Float)
    
    # Önerilen aksiyon
    recommended_action = db.Column(db.Text)
    auto_generated_wo_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=True)
    
    # Durum
    is_acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    acknowledged_at = db.Column(db.DateTime)
    
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    equipment = db.relationship('Equipment', backref='maintenance_alerts')
    trigger = db.relationship('MaintenanceTrigger', backref='alerts')
    work_order = db.relationship('WorkOrder', backref='generated_alerts')
    acknowledger = db.relationship('User', foreign_keys=[acknowledged_by], backref='acknowledged_alerts')
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='resolved_alerts')


# ==================== OPERASYONEL ETKİ YÖNETİMİ ====================

class OperationalImpact(db.Model):
    """Operasyonel etki kaydı - Tren kullanılamazlık yönetimi"""
    __tablename__ = 'operational_impacts'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'), nullable=True)
    failure_id = db.Column(db.Integer, db.ForeignKey('failures.id'), nullable=True)
    
    impact_type = db.Column(db.String(50))  # service_reduction, route_change, full_stop, delay
    impact_severity = db.Column(db.String(20))  # low, medium, high, critical
    
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    
    # Etkilenen hizmetler
    affected_routes = db.Column(db.Text)  # JSON: etkilenen hatlar
    affected_stations = db.Column(db.Text)  # JSON: etkilenen istasyonlar
    service_reduction_percent = db.Column(db.Float, default=0)
    
    # Yolcu etkisi
    estimated_passenger_impact = db.Column(db.Integer, default=0)
    actual_passenger_impact = db.Column(db.Integer)
    
    # Maliyet etkisi
    revenue_loss = db.Column(db.Float, default=0)
    penalty_cost = db.Column(db.Float, default=0)
    recovery_cost = db.Column(db.Float, default=0)
    
    # Müdahale
    mitigation_actions = db.Column(db.Text)
    alternative_service = db.Column(db.Text)
    
    description = db.Column(db.Text)
    root_cause = db.Column(db.Text)
    lessons_learned = db.Column(db.Text)
    
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    equipment = db.relationship('Equipment', backref='operational_impacts')
    work_order = db.relationship('WorkOrder', backref='operational_impacts')
    failure = db.relationship('Failure', backref='operational_impacts')
    reporter = db.relationship('User', backref='reported_impacts')
    
    def calculate_total_cost(self):
        return (self.revenue_loss or 0) + (self.penalty_cost or 0) + (self.recovery_cost or 0)


class FleetAvailability(db.Model):
    """Filo kullanılabilirlik snapshot'ı"""
    __tablename__ = 'fleet_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    snapshot_date = db.Column(db.Date, default=date.today)
    snapshot_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    total_fleet = db.Column(db.Integer, default=0)
    available_fleet = db.Column(db.Integer, default=0)
    in_service = db.Column(db.Integer, default=0)
    in_maintenance = db.Column(db.Integer, default=0)
    in_repair = db.Column(db.Integer, default=0)
    out_of_service = db.Column(db.Integer, default=0)
    
    availability_rate = db.Column(db.Float, default=0)
    service_rate = db.Column(db.Float, default=0)
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==================== BECERİ BAZLI EKİP ATAMA ====================

class SkillMatrix(db.Model):
    """Beceri matrisi - Personel yetkinlikleri"""
    __tablename__ = 'skill_matrix'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    skill_category = db.Column(db.String(50))  # electrical, mechanical, hydraulic, software, safety
    skill_name = db.Column(db.String(100))
    
    proficiency_level = db.Column(db.Integer, default=1)  # 1-5
    certification_required = db.Column(db.Boolean, default=False)
    certification_name = db.Column(db.String(100))
    certification_expiry = db.Column(db.Date)
    
    last_training_date = db.Column(db.Date)
    next_training_due = db.Column(db.Date)
    training_hours = db.Column(db.Float, default=0)
    
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    verified_date = db.Column(db.Date)
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='skill_records')
    verifier = db.relationship('User', foreign_keys=[verified_by])
    
    def get_proficiency_badge(self):
        badges = {
            1: ('secondary', 'Başlangıç'),
            2: ('info', 'Temel'),
            3: ('primary', 'Orta'),
            4: ('success', 'İleri'),
            5: ('warning', 'Uzman')
        }
        return badges.get(self.proficiency_level, ('secondary', 'Bilinmiyor'))


class TeamAssignment(db.Model):
    """Ekip atama kaydı"""
    __tablename__ = 'team_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_orders.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    role_in_team = db.Column(db.String(50))  # lead, member, supervisor, assistant
    assignment_reason = db.Column(db.Text)  # Neden bu kişi seçildi
    
    # Skill match skoru
    skill_match_score = db.Column(db.Float, default=0)  # 0-100
    availability_score = db.Column(db.Float, default=0)  # 0-100
    location_score = db.Column(db.Float, default=0)  # 0-100
    total_score = db.Column(db.Float, default=0)  # Toplam uygunluk skoru
    
    # Zaman
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Çalışma saatleri
    planned_hours = db.Column(db.Float, default=0)
    actual_hours = db.Column(db.Float, default=0)
    
    status = db.Column(db.String(20), default='assigned')  # assigned, in_progress, completed, cancelled
    
    performance_rating = db.Column(db.Integer)  # 1-5
    feedback = db.Column(db.Text)
    
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    work_order = db.relationship('WorkOrder', backref='team_assignments')
    user = db.relationship('User', foreign_keys=[user_id], backref='work_assignments')
    assigner = db.relationship('User', foreign_keys=[assigned_by])

class ServiceStatus(db.Model):
    """Servis durumu modeli - Tramvay servis durumları kaydı"""
    __tablename__ = 'service_status'
    
    id = db.Column(db.Integer, primary_key=True)
    tram_id = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD format
    status = db.Column(db.String(50), nullable=False)  # Servis, Servis Dışı, İşletme Kaynaklı Servis Dışı
    sistem = db.Column(db.String(100), default='')
    aciklama = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    user = db.relationship('User', backref='service_statuses')
    
    __table_args__ = (db.UniqueConstraint('tram_id', 'date', name='unique_tram_date'),)
    
    def __repr__(self):
        return f'<ServiceStatus {self.tram_id} - {self.date}: {self.status}>'