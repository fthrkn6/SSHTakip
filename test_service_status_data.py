"""
Servis Durumu Sistemi Test - Örnek Veri Oluştur
"""

from app import create_app, db
from models import ServiceLog, RootCauseAnalysis, AvailabilityMetrics, Equipment, User
from datetime import datetime, timedelta, date
import random
import json

def create_test_data():
    """Test verileri oluştur"""
    
    app = create_app()
    
    with app.app_context():
        print("🧪 Test Verileri Oluşturuluyor...")
        
        # Araçları kontrol et
        equipment_list = Equipment.query.all()
        if not equipment_list:
            print("⚠️ Sistemde araç bulunmadığı için test verileri oluşturulamaz")
            print("Lütfen önce araç ekleyiniz")
            return
        
        # Admin kullanıcı oluştur
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@test.com', full_name='Admin User')
            admin.set_password('admin')
            admin.role = 'admin'
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin kullanıcı oluşturuldu")
        
        # Her araç için test verileri
        for eq in equipment_list[:3]:  # İlk 3 araç
            tram_id = eq.id_tram
            print(f"\n📊 {tram_id} için test verileri oluşturuluyor...")
            
            # Son 30 gün için log verileri
            systems = ['Elektrik', 'Mekanik', 'HVAC', 'Kapı Sistemi']
            subsystems = {
                'Elektrik': ['Pantograf', 'Muling', 'Traksiyon'],
                'Mekanik': ['Tekerlek', 'Fren', 'Aks'],
                'HVAC': ['Kompressor', 'Fanı', 'Filtre'],
                'Kapı Sistemi': ['Kapı Motor', 'Sensör', 'Kontrol']
            }
            
            statuses = ['operasyonel', 'bakımda', 'servis_dışı']
            
            # 30 gün için random log oluştur
            for days_ago in range(30, 0, -1):
                log_date = datetime.now() - timedelta(days=days_ago)
                
                # Rastgele olaylar
                if random.random() > 0.7:  # %30 ihtimalle sorun
                    system = random.choice(systems)
                    subsystem = random.choice(subsystems[system])
                    
                    log = ServiceLog(
                        tram_id=tram_id,
                        new_status='servis_dışı',
                        sistem=system,
                        alt_sistem=subsystem,
                        reason=f"{system} - {subsystem} arızası",
                        duration_hours=random.randint(1, 8),
                        log_date=log_date,
                        created_by=admin.id
                    )
                    db.session.add(log)
                    
                    # Root cause analizi oluştur
                    rca = RootCauseAnalysis(
                        tram_id=tram_id,
                        sistem=system,
                        alt_sistem=subsystem,
                        failure_description=f"{system} arızası",
                        root_cause=f"{subsystem} arızası tespit edildi",
                        contributing_factors=json.dumps(['Yaşlı parça', 'Bakım yetersizliği']),
                        preventive_actions=json.dumps(['Aylık bakım', 'Parça değişimi']),
                        corrective_actions=json.dumps(['Parça tamiri', 'Kalibrasyonu']),
                        analyzed_by=admin.id,
                        severity_level=random.choice(['orta', 'yüksek']),
                        frequency=random.randint(1, 3),
                        status='closed',
                        analysis_date=log_date
                    )
                    db.session.add(rca)
                    
                    print(f"  ✓ {log_date.strftime('%d.%m.%Y')}: {system} - {subsystem}")
            
            db.session.commit()
            
            # Günlük availability'i hesapla
            for d in range(30):
                target_date = date.today() - timedelta(days=d)
                
                logs = ServiceLog.query.filter(
                    ServiceLog.tram_id == tram_id,
                    db.func.date(ServiceLog.log_date) == target_date
                ).all()
                
                total_hours = 24
                downtime = sum(log.duration_hours or 0 for log in logs)
                operational = max(0, total_hours - downtime)
                availability = (operational / total_hours * 100) if total_hours > 0 else 0
                
                metric = AvailabilityMetrics(
                    tram_id=tram_id,
                    metric_date=target_date,
                    report_period='daily',
                    total_hours=total_hours,
                    operational_hours=operational,
                    downtime_hours=downtime,
                    availability_percentage=round(availability, 2),
                    failure_count=len([l for l in logs if l.new_status != 'operasyonel'])
                )
                
                db.session.add(metric)
            
            db.session.commit()
        
        print("\n✅ Test Verileri Başarıyla Oluşturuldu!")
        print("\nTest Verileri Özeti:")
        print("  • 3 Araç için 30 günlük veri")
        print("  • Her araç için ortalama 10 arıza olayı")
        print("  • Root cause analiz kayıtları")
        print("  • Günlük availability metrikleri")
        print("\n📊 Servis durumu sayfasını kontrol edebilirsiniz:")
        print("   http://localhost:5000/servis/durumu")

if __name__ == '__main__':
    create_test_data()
