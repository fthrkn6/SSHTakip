"""
Availability Metrikleri Hesapla - AvailabilityMetrics tablosunu doldur
ServiceStatus + Failure verilerinden otomatik hesaplama
"""
import os
import sys
from datetime import datetime, date, timedelta

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

from app import create_app, db
from models import ServiceStatus, AvailabilityMetrics, Equipment, Failure
from sqlalchemy import func

app = create_app()

def calculate_daily_availability(tram_id, target_date, project_code='belgrad'):
    """Günlük availability metriklerini hesapla"""
    
    # O gün için servis durumunu kontrol et
    status_record = ServiceStatus.query.filter_by(
        tram_id=tram_id,
        date=str(target_date),
        project_code=project_code
    ).first()
    
    if not status_record:
        # Eğer kayıt yoksa, aktif olarak kabul et
        operational_hours = 24.0
        downtime_hours = 0.0
        availability = 100.0
    else:
        # Status'e göre saatleri ayarla
        status = status_record.status.lower() if status_record.status else ''
        
        if 'dışı' in status or 'ariza' in status:
            # Tamamen serviste
            operational_hours = 0.0
            downtime_hours = 24.0
            availability = 0.0
        elif 'işletme' in status:
            # Kısmi işletme
            operational_hours = 12.0
            downtime_hours = 12.0
            availability = 50.0
        else:
            # Normal işletme
            operational_hours = 24.0
            downtime_hours = 0.0
            availability = 100.0
    
    # O gün için failure sayısını kontrol et
    failure_count = Failure.query.filter(
        Failure.tram_id == tram_id,
        func.date(Failure.failure_date) == target_date
    ).count()
    
    return {
        'operational_hours': operational_hours,
        'downtime_hours': downtime_hours,
        'availability_percentage': availability,
        'failure_count': failure_count
    }

with app.app_context():
    # Tüm projectler ve tram_id'ler için metrik hesapla
    projects = ['belgrad', 'iasi', 'timisoara', 'kayseri', 'kocaeli', 'gebze']
    
    # Son 90 günü hesapla
    for days_back in range(90):
        target_date = date.today() - timedelta(days=days_back)
        
        for project in projects:
            # O zamanki tüm araçları al
            equipments = Equipment.query.filter_by(
                parent_id=None,
                project_code=project
            ).all()
            
            for equipment in equipments:
                tram_id = equipment.equipment_code
                
                # Daha önce hesaplanmış mı kontrol et
                existing = AvailabilityMetrics.query.filter_by(
                    tram_id=tram_id,
                    metric_date=target_date,
                    report_period='daily'
                ).first()
                
                if existing:
                    continue  # Zaten hesaplanmış
                
                # Hesapla
                metrics = calculate_daily_availability(tram_id, target_date, project)
                
                # Kaydet
                metric_record = AvailabilityMetrics(
                    tram_id=tram_id,
                    metric_date=target_date,
                    operational_hours=metrics['operational_hours'],
                    downtime_hours=metrics['downtime_hours'],
                    availability_percentage=metrics['availability_percentage'],
                    failure_count=metrics['failure_count'],
                    report_period='daily'
                )
                
                db.session.add(metric_record)
    
    # Commit
    try:
        db.session.commit()
        print("✅ AvailabilityMetrics hesaplama tamamlandı")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Hata: {e}")
