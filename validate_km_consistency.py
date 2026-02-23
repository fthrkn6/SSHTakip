"""
KM Verilerinin Tutarlılığını Kontrol Et
Equipment.current_km vs km_data.json
"""
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

from app import create_app, db
from utils_km_manager import KMDataManager

app = create_app()

with app.app_context():
    projects = ['belgrad', 'iasi', 'timisoara', 'kayseri', 'kocaeli', 'gebze']
    
    for project in projects:
        print(f"\n{'='*60}")
        print(f"[CHECK] Proje: {project.upper()}")
        print(f"{'='*60}")
        
        # Kontrol et
        result = KMDataManager.validate_km_consistency(project)
        
        print(f"[INFO] Toplam tramvay: {result.get('total_trams', 0)}")
        print(f"[STATUS] Tutarli: {result['consistent']}")
        
        if result['mismatches']:
            print(f"\n[WARNING] Tutarsizliklar ({len(result['mismatches'])} adet):")
            for mm in result['mismatches'][:5]:  # İlk 5'i göster
                print(f"   Tramvay {mm['tram_id']}: Equipment={mm['equipment_km']} vs JSON={mm['json_km']}")
            
            if len(result['mismatches']) > 5:
                print(f"   ... ve {len(result['mismatches']) - 5} tane daha")
            
            # Düzelt
            print(f"\n[ACTION] Duzeltme baslaniyor...")
            if KMDataManager.repair_km_consistency(project):
                print(f"[OK] {project} KM verileri senkronize edildi!")
                
                # Sonra kontrol et
                result_after = KMDataManager.validate_km_consistency(project)
                if result_after['consistent']:
                    print(f"[VERIFY] Senkronizasyon basarili - Tum veriler tutarli!")
                else:
                    print(f"[WARNING] Hala {len(result_after['mismatches'])} tutarsizlik var")
            else:
                print(f"[ERROR] {project} senkronizasyon basarisiz")
        else:
            print(f"[OK] Tum veriler tutarli!")
            
            if result.get('note'):
                print(f"   Not: {result['note']}")
    
    print(f"\n{'='*60}")
    print(f"[COMPLETE] KONTROL VE SENKRONIZASYON TAMAMLANDI")
    print(f"{'='*60}")
