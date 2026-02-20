#!/usr/bin/env python
"""
Dashboard Veri Akışı Debug Script
=================================
Stats dictionary'deki verilerin kaynağını adım adım kontrol et
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from models import Equipment, ServiceStatus
from utils.project_manager import ProjectManager
from datetime import date
import pandas as pd

def debug_dashboard_flow(project_code='kayseri'):
    """Dashboard veri akışını debug et"""
    
    with app.app_context():
        print("="*80)
        print(f"DASHBOARD VERİ AKIŞI DEBUG - {project_code.upper()}")
        print("="*80)
        
        # ====== ADIM 1: TRAMVAY LİSTESİNİ AL ======
        print("\n📍 ADIM 1: TRAMVAY LİSTESİ (get_tram_ids_from_veriler)")
        print("-"*80)
        
        # Veriler.xlsx dosyasını bul
        veriler_file = ProjectManager.get_veriler_file(project_code)
        print(f"Veriler.xlsx path: {veriler_file}")
        
        if veriler_file and os.path.exists(veriler_file):
            print(f"✅ Dosya var")
            try:
                # Excel'i oku
                df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
                print(f"\nSayfa2 sütunları: {list(df.columns)}")
                print(f"Sayfa2 satır sayısı: {len(df)}")
                
                # İlk 5 satırı göster
                print("\nİlk 5 satır:")
                print(df.head())
                
                # tram_id sütununu bul
                tram_id_col = None
                for col in df.columns:
                    if 'tram' in col.lower() or 'equipment' in col.lower():
                        tram_id_col = col
                        print(f"\n✅ Bulunan sütun: '{col}'")
                        break
                
                if tram_id_col:
                    tram_ids = df[tram_id_col].dropna().unique().tolist()
                    print(f"Okunan tramvay sayısı: {len(tram_ids)}")
                    print(f"İlk 5 tram_id: {tram_ids[:5]}")
                else:
                    print("❌ Tram ID sütunu bulunamadı!")
                    
            except Exception as e:
                print(f"❌ Excel okuma hatası: {e}")
        else:
            print(f"❌ Veriler.xlsx bulunamadı")
        
        # ====== ADIM 2: EQUIPMENT TABLOSUNDAN TRAMVAY AL ======
        print("\n📍 ADIM 2: EQUIPMENT TABLOSU")
        print("-"*80)
        
        tramvaylar = Equipment.query.filter_by(
            parent_id=None,
            project_code=project_code
        ).order_by(Equipment.equipment_code).all()
        
        print(f"Equipment tablosundan bulunan tramvay: {len(tramvaylar)}")
        
        if tramvaylar:
            print(f"İlk 5 tramvay:")
            for i, t in enumerate(tramvaylar[:5]):
                print(f"  {i+1}. {t.equipment_code}: status='{t.status}', name='{t.name}'")
        else:
            print("❌ HATA: Equipment tablosu boş!")
        
        # ====== ADIM 3: STATUS KONTROLÜ ======
        print("\n📍 ADIM 3: STATUS DAĞILIMI")
        print("-"*80)
        
        status_counts = {}
        for t in tramvaylar:
            status = t.status if t.status else 'NULL/None'
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("Status dağılımı:")
        for status, count in status_counts.items():
            print(f"  '{status}': {count}")
        
        # ====== ADIM 4: BUGÜNÜN SERVİCE STATUS KAYDI ======
        print("\n📍 ADIM 4: BUGÜN'ÜN SERVİCE STATUS KAYDI")
        print("-"*80)
        
        today = str(date.today())
        print(f"Bugün: {today}")
        
        # Tüm projeler için ServiceStatus'ü kontrol et
        all_today_records = ServiceStatus.query.filter_by(date=today).all()
        print(f"Tüm projeler için ServiceStatus ({today}): {len(all_today_records)}")
        
        # Bu proje için
        project_records = [r for r in all_today_records if r.tram_id]
        print(f"Geçerli tram_id'li kayıt: {len(project_records)}")
        
        if project_records:
            print("İlk 5 kayıt:")
            for i, r in enumerate(project_records[:5]):
                print(f"  {i+1}. tram_id={r.tram_id}, status='{r.status}'")
        else:
            print("⚠️ UYARI: ServiceStatus tablosu boş (tüm tramvaylar AKTIF sayılacak)")
        
        # ====== ADIM 5: STATS HESAPLAMA ======
        print("\n📍 ADIM 5: STATS HESAPLAMA SİMÜLASYONU")
        print("-"*80)
        
        aktif_count = 0
        isletme_count = 0
        ariza_count = 0
        
        for t in tramvaylar:
            # Equipment status'unu al
            equipment_status = t.status if t.status else 'aktif'
            
            # Status belirle (dashboard.py'deki aynı logic)
            if equipment_status and equipment_status.lower() in ['ariza', 'servis_disi', 'disi']:
                ariza_count += 1
                status_display = "ARIZA"
            elif equipment_status and equipment_status.lower() in ['bakim', 'isletme', 'işletme']:
                isletme_count += 1
                status_display = "İŞLETME"
            else:
                aktif_count += 1
                status_display = "AKTIF"
            
            if len(tramvaylar) <= 10:  # Küçük fleet için detayını göster
                print(f"  {t.equipment_code}: {status_display}")
        
        print(f"\nHesaplanan Sayılar:")
        print(f"  Aktif: {aktif_count}")
        print(f"  İşletme: {isletme_count}")
        print(f"  Arıza: {ariza_count}")
        print(f"  Toplam: {len(tramvaylar)}")
        
        total_tram = len(tramvaylar) if tramvaylar else 1
        kullanilabilir = aktif_count + isletme_count
        fleet_availability = round(kullanilabilir / total_tram * 100, 1) if total_tram > 0 else 0
        
        print(f"  Fleet Kullanılabilirlik: ({aktif_count} + {isletme_count}) / {total_tram} * 100 = {fleet_availability}%")
        
        # ====== ÖZET ======
        print("\n" + "="*80)
        print("ÖZET VE ÖNERİLER")
        print("="*80)
        
        if len(tramvaylar) == 0:
            print("\n❌ SORUN: Equipment tablosu boş!")
            print("→ data/{0}/Veriler.xlsx'te doğru şekilde tram_id'ler tanımlanmalı".format(project_code))
            print("→ Ya da Equipment tablosuna data yüklenmeli")
        
        if len(status_counts) == 1 and 'NULL/None' in status_counts:
            print("\n⚠️ UYARI: Tüm tramvayların status=NULL")
            print("→ Tümü AKTIF sayılıyor (default behavior)")
        
        if len(all_today_records) == 0:
            print("\n⚠️ UYARI: ServiceStatus tablosu boş")
            print("→ Bugün'ün durumu Equipment.status'dan okunuyor")
        
        print("\n✅ SONUÇ: Stats dictionary şu değerleri içerecek:")
        print(f"  - total_tramvay: {len(tramvaylar)}")
        print(f"  - aktif_servis: {aktif_count}")
        print(f"  - bakimda: {isletme_count}")
        print(f"  - arizali: {ariza_count}")
        print(f"  - fleet_availability: {fleet_availability}%")
        
        print("\n" + "="*80)

if __name__ == '__main__':
    # Test et
    print("\n🔍 KAYSERI KONTROL:")
    debug_dashboard_flow('kayseri')
    
    print("\n\n🔍 BELGRAD KONTROL:")
    debug_dashboard_flow('belgrad')
