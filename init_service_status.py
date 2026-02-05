"""
Servis Durumu Sistemini başlat ve initialize et
"""

import os
from app import create_app, db
from models import AvailabilityMetrics, ServiceLog, RootCauseAnalysis

def init_service_status_system():
    """Servis durumu sistemini initialize et"""
    
    app = create_app()
    
    with app.app_context():
        # Log klasörlerini oluştur
        log_dirs = [
            'logs',
            'logs/availability',
            'logs/rapor_cikti'
        ]
        
        for log_dir in log_dirs:
            os.makedirs(log_dir, exist_ok=True)
            print(f"✓ Klasör oluşturuldu: {log_dir}")
        
        # Tabloları oluştur
        try:
            db.create_all()
            print("✓ Veritabanı tabloları başarıyla oluşturuldu")
            
            # Örnek availability metriği oluştur
            count = AvailabilityMetrics.query.count()
            if count == 0:
                print("✓ Availability metrikleri hazırlanıyor...")
                # Zaten route'larda otomatik oluşacak
            
            print("\n✅ Servis Durumu Sistemi başarıyla initialize edildi!")
            print("\nSistem Özellikleri:")
            print("  • 📊 Gerçek zamanlı availability takibi")
            print("  • 📈 Günlük, Haftalik, Aylık, 3 Aylık, 6 Aylık, Yıllık ve Total analiz")
            print("  • 🔍 Sistem ve alt sistem bazında Root Cause Analizi")
            print("  • 📋 Kapsamlı Excel raporlama")
            print("  • 📁 Otomatik log kaydı (logs/availability/)")
            print("  • 💾 Raporlar: logs/rapor_cikti/")
            print("  • 🎯 Sticky Export butonu (sol alt)")
            print("\nErişim: http://localhost:5000/servis/durumu")
            
        except Exception as e:
            print(f"✗ Hata: {str(e)}")
            raise

if __name__ == '__main__':
    init_service_status_system()
