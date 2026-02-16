#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test RCA with full date range"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, '.')

from app import create_app
from utils_root_cause_analysis import RootCauseAnalyzer

def test_rca_full():
    """Test RCA with wider date range"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("🔍 ROOT CAUSE ANALYSIS - KAPSAMLI TEST (6 AY VERİ)")
        print("=" * 80)
        
        # 6 aylık veri analizi
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        
        print(f"\n📅 Analiz Dönemi: {start_date} → {end_date} (6 ay)")
        
        try:
            # Analiz yap
            print("\n⏳ Veriler analiz ediliyor (sistem ve alt sistem bazında)...")
            analysis = RootCauseAnalyzer.analyze_service_disruptions(
                start_date=start_date,
                end_date=end_date
            )
            
            print(f"\n✅ ANALIZ SONUÇLARI:")
            print(f"   📊 Toplam Servis Dışı Gün: {analysis['total_records']}")
            print(f"   🔧 İncelenen Sistemler: {len(analysis['sistem_analysis'])}")
            print(f"   🚊 Etkilenen Araçlar: {len(analysis['tram_analysis'])}")
            
            # Risk analizi
            if analysis['total_records'] > 0:
                print(f"\n⚠️  RISK ANALİZİ:")
                for i, (sistem, data) in enumerate(analysis['top_systems'][:10], 1):
                    percentage = (data['days'] / analysis['total_records'] * 100)
                    
                    if percentage > 30:
                        risk = "🔴 KRİTİK"
                    elif percentage > 15:
                        risk = "🟠 YÜKSEK"
                    else:
                        risk = "🟢 DÜŞÜK"
                    
                    print(f"   {i:2}. {sistem:25} {data['days']:3} gün ({percentage:5.1f}%) {risk}")
            
            # Alt sistem detayları
            if analysis['sistem_analysis']:
                print(f"\n🔨 ALT SİSTEM DETAYLARI (İlk 3 Sistem):")
                for sistem, data in list(analysis['sistem_analysis'].items())[:3]:
                    print(f"\n   → {sistem.upper()} ({data['days']} gün, {data['count']} olay)")
                    for alt_sistem, alt_data in sorted(
                        data['alt_sistemler'].items(),
                        key=lambda x: x[1]['days'],
                        reverse=True
                    )[:5]:
                        print(f"      • {alt_sistem:30} - {alt_data['days']} gün / {alt_data['count']} olay")
            
            # En çok etkilenen araçlar
            if analysis['tram_analysis']:
                print(f"\n🚊 EN ÇOK ETKILENEN ARAÇLAR:")
                for tram_id, data in sorted(
                    analysis['tram_analysis'].items(),
                    key=lambda x: x[1]['total_days_out'],
                    reverse=True
                )[:10]:
                    sistemler = ', '.join(sorted(data['sistemler']))
                    print(f"   • {tram_id:10} - {data['total_days_out']:2} gün servis dışı ({sistemler})")
            
            # Excel oluştur
            print(f"\n⏳ Excel raporu oluşturuluyor...")
            filepath = RootCauseAnalyzer.generate_rca_excel(analysis)
            
            file_size = Path(filepath).stat().st_size / 1024
            print(f"\n✅ EXCEL RAPORU OLUŞTURULDU:")
            print(f"   📁 Dosya: {filepath}")
            print(f"   📊 Boyut: {file_size:.1f} KB")
            
            print("\n" + "=" * 80)
            print("✅ TEST BAŞARILI!")
            print("   Root Cause Analysis sistemi tam olarak çalışıyor.")
            print("   'Root Cause Analizi' butonuna tıklayarak raporu indirebilirsiniz.")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            print(f"\n❌ HATA: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_rca_full()
    sys.exit(0 if success else 1)
