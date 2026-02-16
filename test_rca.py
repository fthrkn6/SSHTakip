#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Root Cause Analysis functionality"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add current directory to path
sys.path.insert(0, '.')

# Import Flask app to create context
from app import create_app

# Import the analyzer
from utils_root_cause_analysis import RootCauseAnalyzer

def test_rca():
    """Test RCA analysis and Excel generation"""
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("🔍 ROOT CAUSE ANALYSIS TEST")
        print("=" * 70)
        
        # Analiz parametreleri
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        print(f"\n📅 Analiz Dönemi: {start_date} → {end_date}")
        print(f"🔎 Sistem/Alt Sistem Verilerini Analiz Ediliyor...")
        
        try:
            # Analiz yap
            print("\n⏳ Veriler analiz ediliyor...")
            analysis = RootCauseAnalyzer.analyze_service_disruptions(
                start_date=start_date,
                end_date=end_date
            )
            
            print(f"\n✅ Analiz Tamamlandı:")
            print(f"   - Toplam Servis Dışı Gün: {analysis['total_records']}")
            print(f"   - İncelenen Sistemler: {len(analysis['sistem_analysis'])}")
            print(f"   - Etkilenen Araçlar: {len(analysis['tram_analysis'])}")
            
            # Top sistemleri göster
            if analysis['top_systems']:
                print(f"\n📊 En Çok Etkilenen Sistemler (Top 5):")
                for i, (sistem, data) in enumerate(analysis['top_systems'][:5], 1):
                    percentage = (data['days'] / analysis['total_records'] * 100) if analysis['total_records'] > 0 else 0
                    print(f"   {i}. {sistem}: {data['days']} gün ({percentage:.1f}%) - {data['count']} olay")
            
            # Sistem detayları
            print(f"\n📋 Sistem Detayları:")
            for sistem, data in list(analysis['sistem_analysis'].items())[:5]:
                print(f"   • {sistem}: {data['days']} gün, {data['affected_tram_count']} araç")
                for alt_sistem, alt_data in list(data['alt_sistemler'].items())[:3]:
                    print(f"      → {alt_sistem}: {alt_data['days']} gün")
            
            # Excel oluştur
            print(f"\n⏳ Excel raporu oluşturuluyor...")
            filepath = RootCauseAnalyzer.generate_rca_excel(analysis)
            
            file_size = Path(filepath).stat().st_size / 1024  # KB
            print(f"✅ Excel raporu oluşturuldu:")
            print(f"   📁 Dosya: {filepath}")
            print(f"   📊 Boyut: {file_size:.1f} KB")
            
            print("\n" + "=" * 70)
            print("✅ TEST BAŞARILI - RCA SİSTEMİ ÇALIŞIYOR")
            print("=" * 70)
            
            return True
            
        except Exception as e:
            print(f"\n❌ HATA: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_rca()
    sys.exit(0 if success else 1)
