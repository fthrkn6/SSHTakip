"""
Örnek veri oluşturma scripti
CMMS sistemini test verileriyle doldurur
"""

from datetime import datetime, timedelta
from app import create_app, db
from models import (User, Equipment, MaintenancePlan, WorkOrder, 
                   MaintenanceLog, SensorData, Failure, Inventory, KPI)
import random

def create_sample_data():
    app = create_app()
    
    with app.app_context():
        print("Örnek veriler oluşturuluyor...")
        
        # Veritabanını temizle
        db.drop_all()
        db.create_all()
        
        # 1. Kullanıcılar
        print("Kullanıcılar oluşturuluyor...")
        admin = User(
            username='admin',
            email='admin@cmms.local',
            full_name='Yönetici',
            role='admin',
            department='IT'
        )
        admin.set_password('admin123')
        
        manager = User(
            username='manager',
            email='manager@cmms.local',
            full_name='Bakım Müdürü',
            role='manager',
            department='Maintenance'
        )
        manager.set_password('manager123')
        
        tech1 = User(
            username='tech1',
            email='tech1@cmms.local',
            full_name='Ahmet Yılmaz',
            role='technician',
            department='Maintenance'
        )
        tech1.set_password('tech123')
        
        tech2 = User(
            username='tech2',
            email='tech2@cmms.local',
            full_name='Mehmet Demir',
            role='technician',
            department='Maintenance'
        )
        tech2.set_password('tech123')
        
        db.session.add_all([admin, manager, tech1, tech2])
        db.session.commit()
        
        # 2. Ekipmanlar
        print("Ekipmanlar oluşturuluyor...")
        trains = []
        for i in range(1, 6):
            train = Equipment(
                equipment_code=f'TRN-{i:03d}',
                name=f'Tramvay {i}',
                equipment_type='train',
                manufacturer='Siemens',
                model='Avenio',
                serial_number=f'SN-TRN-{i:04d}',
                manufacture_date=datetime(2020, 1, 1),
                commissioning_date=datetime(2020, 6, 1),
                location='Kayseri',
                status='operational',
                criticality='high',
                total_operating_hours=random.randint(5000, 15000),
                total_distance_km=random.randint(50000, 150000)
            )
            trains.append(train)
            db.session.add(train)
        
        db.session.commit()
        
        # Bileşenler (her tren için)
        components = []
        for train in trains:
            # Motor
            motor = Equipment(
                equipment_code=f'{train.equipment_code}-MOT',
                name=f'{train.name} - Motor',
                equipment_type='motor',
                manufacturer='Siemens',
                model='1TB2352',
                status='operational',
                criticality='critical',
                parent_id=train.id
            )
            
            # Fren sistemi
            brake = Equipment(
                equipment_code=f'{train.equipment_code}-BRK',
                name=f'{train.name} - Fren Sistemi',
                equipment_type='brake',
                manufacturer='Knorr-Bremse',
                model='KB-EP2',
                status='operational',
                criticality='critical',
                parent_id=train.id
            )
            
            # Kapı sistemi
            door = Equipment(
                equipment_code=f'{train.equipment_code}-DOOR',
                name=f'{train.name} - Kapı Sistemi',
                equipment_type='door',
                manufacturer='IFE',
                model='Auto-400',
                status='operational',
                criticality='medium',
                parent_id=train.id
            )
            
            components.extend([motor, brake, door])
            db.session.add_all([motor, brake, door])
        
        db.session.commit()
        
        # 3. Bakım Planları
        print("Bakım planları oluşturuluyor...")
        for train in trains:
            # KM bazlı bakımlar
            # 10.000 KM Bakımı (A Bakımı)
            km_10k_plan = MaintenancePlan(
                equipment_id=train.id,
                plan_name=f'{train.name} - 10.000 KM Bakımı (A Bakımı)',
                maintenance_type='preventive',
                frequency='km_based',
                interval_km=10000,
                estimated_duration_hours=4,
                priority='high',
                description='Temel kontroller ve yağlama işlemleri',
                procedures=[
                    'Yağ seviye kontrolü',
                    'Fren balatası kontrolü',
                    'Lastik basınç kontrolü',
                    'Genel temizlik',
                    'Emniyetli test sürüşü'
                ],
                estimated_cost=500.0
            )
            
            # 25.000 KM Bakımı (B Bakımı)
            km_25k_plan = MaintenancePlan(
                equipment_id=train.id,
                plan_name=f'{train.name} - 25.000 KM Bakımı (B Bakımı)',
                maintenance_type='preventive',
                frequency='km_based',
                interval_km=25000,
                estimated_duration_hours=8,
                priority='high',
                description='Orta seviye bakım ve parça değişimleri',
                procedures=[
                    'Motor yağ değişimi',
                    'Fren hidroliği kontrolü',
                    'Elektrik sistemleri kontrolü',
                    'Süspansiyon kontrolü',
                    'Klima sistemi bakımı',
                    'Test sürüşü ve kalibrasyon'
                ],
                estimated_cost=1500.0
            )
            
            # 50.000 KM Bakımı (C Bakımı)
            km_50k_plan = MaintenancePlan(
                equipment_id=train.id,
                plan_name=f'{train.name} - 50.000 KM Bakımı (C Bakımı)',
                maintenance_type='preventive',
                frequency='km_based',
                interval_km=50000,
                estimated_duration_hours=16,
                priority='critical',
                description='Kapsamlı bakım ve büyük revizyonlar',
                procedures=[
                    'Tam motor kontrolü ve revizyonu',
                    'Transmisyon sistemi kontrolü',
                    'Fren sistemi revizyonu',
                    'Elektrik panoları kontrolü',
                    'Tüm sensörlerin kalibrasyonu',
                    'Kapı mekanizmaları revizyonu',
                    'Güvenlik sistemleri testi',
                    'Detaylı test sürüşü'
                ],
                estimated_cost=4000.0
            )
            
            # 100.000 KM Bakımı (D Bakımı)
            km_100k_plan = MaintenancePlan(
                equipment_id=train.id,
                plan_name=f'{train.name} - 100.000 KM Bakımı (D Bakımı)',
                maintenance_type='preventive',
                frequency='km_based',
                interval_km=100000,
                estimated_duration_hours=32,
                priority='critical',
                description='Büyük revizyonlar ve kritik parça değişimleri',
                procedures=[
                    'Motor komple revizyonu',
                    'Şanzıman ve vites kutusu kontrolü',
                    'Diferansiyel bakımı',
                    'Tüm elektronik sistemlerin revizyonu',
                    'Pantograf sistemi revizyonu',
                    'Bojiler ve tekerlek setleri kontrolü',
                    'Klima kompresörü revizyonu',
                    'Tüm güvenlik sistemlerinin detaylı testi',
                    'Komple araç kalibrasyonu'
                ],
                estimated_cost=10000.0
            )
            
            # 200.000 KM Bakımı (E Bakımı - Genel Revizyon)
            km_200k_plan = MaintenancePlan(
                equipment_id=train.id,
                plan_name=f'{train.name} - 200.000 KM Bakımı (E Bakımı - Genel Revizyon)',
                maintenance_type='preventive',
                frequency='km_based',
                interval_km=200000,
                estimated_duration_hours=80,
                priority='critical',
                description='Tam genel revizyon - Tramvayın komple yenilenmesi',
                procedures=[
                    'Motor komple sökme ve yenileme',
                    'Tüm mekanik aksamların revizyonu',
                    'Elektrik sistemleri komple yenilenmesi',
                    'Karoser ve gövde kontrolü',
                    'Yolcu koltuklarının bakımı/değişimi',
                    'Tüm güvenlik ekipmanlarının yenilenmesi',
                    'Bilgisayar sistemleri güncelleme',
                    'Tam boya ve kaplama kontrolü',
                    'Komple fonksiyon testleri',
                    'Fabrika çıkış kalibrasyon seviyesine getirme'
                ],
                estimated_cost=30000.0
            )
            
            db.session.add_all([km_10k_plan, km_25k_plan, km_50k_plan, km_100k_plan, km_200k_plan])
            
            # Günlük kontrol
            daily_plan = MaintenancePlan(
                equipment_id=train.id,
                plan_name=f'{train.name} - Günlük Kontrol',
                maintenance_type='preventive',
                frequency='daily',
                frequency_value=1,
                estimated_duration_hours=0.5,
                priority='high',
                description='Günlük görsel kontrol ve temel işlevsellik testi'
            )
            
            # Aylık bakım
            monthly_plan = MaintenancePlan(
                equipment_id=train.id,
                plan_name=f'{train.name} - Aylık Bakım',
                maintenance_type='preventive',
                frequency='monthly',
                frequency_value=1,
                estimated_duration_hours=4,
                priority='high',
                description='Detaylı kontrol ve yağlama işlemleri'
            )
            
            # KM bazlı bakım
            km_plan = MaintenancePlan(
                equipment_id=train.id,
                plan_name=f'{train.name} - 10000 KM Bakımı',
                maintenance_type='preventive',
                frequency='km_based',
                frequency_value=10000,
                estimated_duration_hours=8,
                priority='critical',
                description='Kapsamlı bakım ve parça değişimi'
            )
            
            db.session.add_all([daily_plan, monthly_plan, km_plan])
        
        db.session.commit()
        
        # 4. İş Emirleri
        print("İş emirleri oluşturuluyor...")
        for i in range(20):
            equipment = random.choice(trains + components)
            
            wo = WorkOrder(
                work_order_number=f'WO-{datetime.now().strftime("%Y%m")}-{i+1:04d}',
                equipment_id=equipment.id,
                title=random.choice([
                    'Rutin Bakım',
                    'Arıza Onarımı',
                    'Yağlama İşlemi',
                    'Parça Değişimi',
                    'Güvenlik Kontrolü'
                ]),
                description=f'{equipment.name} için planlı bakım',
                work_type=random.choice(['preventive', 'corrective', 'inspection']),
                priority=random.choice(['low', 'medium', 'high', 'critical']),
                status=random.choice(['pending', 'scheduled', 'in_progress', 'completed']),
                scheduled_start=datetime.now() + timedelta(days=random.randint(-10, 30)),
                assigned_to=random.choice([tech1.id, tech2.id]),
                created_by=manager.id,
                estimated_cost=random.randint(500, 5000)
            )
            
            db.session.add(wo)
        
        db.session.commit()
        
        # 5. Sensör Verileri
        print("Sensör verileri oluşturuluyor...")
        for train in trains:
            for hours_ago in range(24, 0, -1):
                timestamp = datetime.now() - timedelta(hours=hours_ago)
                
                # Sıcaklık
                temp = SensorData(
                    equipment_id=train.id,
                    timestamp=timestamp,
                    sensor_type='temperature',
                    sensor_location='motor',
                    value=random.uniform(65, 85),
                    unit='°C'
                )
                
                # Titreşim
                vibration = SensorData(
                    equipment_id=train.id,
                    timestamp=timestamp,
                    sensor_type='vibration',
                    sensor_location='bogie',
                    value=random.uniform(0.5, 2.5),
                    unit='mm/s'
                )
                
                db.session.add_all([temp, vibration])
        
        db.session.commit()
        
        # 6. Arızalar
        print("Arıza kayıtları oluşturuluyor...")
        for i in range(10):
            failure = Failure(
                equipment_id=random.choice(trains).id,
                failure_code=f'FLR-{datetime.now().year}-{i+1:04d}',
                failure_type=random.choice(['Electrical', 'Mechanical', 'Software']),
                severity=random.choice(['minor', 'major', 'critical']),
                failure_date=datetime.now() - timedelta(days=random.randint(1, 90)),
                detection_method=random.choice(['inspection', 'sensor', 'operator_report']),
                description='Arıza açıklaması',
                downtime_hours=random.uniform(1, 24),
                resolved=random.choice([True, False])
            )
            db.session.add(failure)
        
        db.session.commit()
        
        # 7. Envanter
        print("Envanter kayıtları oluşturuluyor...")
        parts = [
            ('FLT-001', 'Motor Filtresi', 'Filter', 50, 10, 20),
            ('BRK-PAD-001', 'Fren Balatası', 'Brake', 30, 5, 10),
            ('OIL-001', 'Motor Yağı 5L', 'Lubrication', 100, 20, 30),
            ('BELT-001', 'V-Kayış', 'Belt', 25, 5, 10),
            ('SEN-TEMP-001', 'Sıcaklık Sensörü', 'Sensor', 15, 3, 5),
        ]
        
        for part_no, name, category, qty, min_qty, reorder_qty in parts:
            part = Inventory(
                part_number=part_no,
                part_name=name,
                category=category,
                manufacturer='OEM',
                quantity_in_stock=qty,
                minimum_stock_level=min_qty,
                reorder_quantity=reorder_qty,
                unit_cost=random.uniform(50, 500),
                currency='TRY',
                location='Merkez Depo'
            )
            db.session.add(part)
        
        db.session.commit()
        
        # 8. KPI Verileri
        print("KPI verileri oluşturuluyor...")
        for days_ago in range(30, 0, -5):
            kpi_date = datetime.now().date() - timedelta(days=days_ago)
            
            kpi = KPI(
                calculation_date=kpi_date,
                equipment_id=None,  # Genel KPI
                mtbf=random.uniform(500, 800),
                mttr=random.uniform(2, 6),
                availability=random.uniform(92, 98),
                reliability=random.uniform(94, 99),
                preventive_maintenance_compliance=random.uniform(85, 95),
                maintenance_cost=random.uniform(50000, 100000),
                total_downtime_hours=random.uniform(10, 50),
                total_operating_hours=random.uniform(3000, 4000)
            )
            db.session.add(kpi)
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("Örnek veriler başarıyla oluşturuldu!")
        print("="*50)
        print("\nGiriş Bilgileri:")
        print("-" * 50)
        print("Admin    : admin / admin123")
        print("Manager  : manager / manager123")
        print("Teknisyen: tech1 / tech123")
        print("Teknisyen: tech2 / tech123")
        print("-" * 50)
        print("\nOluşturulan Veriler:")
        print(f"- {User.query.count()} Kullanıcı")
        print(f"- {Equipment.query.count()} Ekipman")
        print(f"- {MaintenancePlan.query.count()} Bakım Planı")
        print(f"- {WorkOrder.query.count()} İş Emri")
        print(f"- {SensorData.query.count()} Sensör Verisi")
        print(f"- {Failure.query.count()} Arıza Kaydı")
        print(f"- {Inventory.query.count()} Envanter Kalemi")
        print(f"- {KPI.query.count()} KPI Kaydı")
        print("="*50)


if __name__ == '__main__':
    create_sample_data()
