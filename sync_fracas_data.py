"""
FRACAS Excel Verilerini CMMS Veritabanına Senkronize Et
Bu script Excel'deki FRACAS verilerini okur ve veritabanını günceller
"""

import pandas as pd
from datetime import datetime
from app import create_app
from models import db, Equipment, Failure, User

def sync_fracas_data():
    """Excel'den FRACAS verilerini veritabanına aktar"""
    
    app = create_app()
    
    with app.app_context():
        # Excel dosyasını oku
        excel_path = r'C:\Users\ferki\Desktop\cmms_system\data\BEL25_FRACAS(Hata Raporlama Analizi ve Düzeltici Aksiyon Sitemi) Formu - 2025.12.3 S.xlsx'
        
        df = pd.read_excel(excel_path, sheet_name='FRACAS', header=3)
        df.columns = df.columns.str.replace('\n', ' ', regex=False).str.strip()
        df = df[df['FRACAS ID'].notna()]
        
        print(f"Toplam {len(df)} FRACAS kaydı bulundu")
        
        # Araç numaralarını çıkar ve temizle
        arac_col = [c for c in df.columns if 'Araç Numarası' in c][0]
        araclar = df[arac_col].dropna().unique()
        
        print(f"\n=== ARAÇLAR ({len(araclar)} adet) ===")
        
        # Mevcut tramvayları sil ve yeniden oluştur
        Equipment.query.filter_by(equipment_type='tramvay').delete()
        db.session.commit()
        
        # Her araç için Equipment oluştur
        vehicle_map = {}  # araç_no -> equipment_id mapping
        
        for arac in araclar:
            arac_str = str(arac).strip()
            # Araç numarasını temizle: "1533(3)" -> "1533"
            arac_no = arac_str.split('(')[0] if '(' in arac_str else arac_str
            
            # Araç kilometresini bul
            arac_df = df[df[arac_col] == arac]
            km_col = [c for c in df.columns if 'Kilometresi' in c][0]
            km = arac_df[km_col].dropna().max() if not arac_df[km_col].dropna().empty else 0
            
            equipment = Equipment(
                equipment_code=f'TRN-{arac_no}',
                name=f'Tramvay {arac_no}',
                equipment_type='tramvay',
                manufacturer='Bozankaya',
                model='Tramvay',
                serial_number=arac_str,
                location='Hat',
                status='aktif',
                criticality='high',
                hierarchy_level=1,
                total_km=float(km) if pd.notna(km) else 0
            )
            db.session.add(equipment)
            db.session.flush()  # ID almak için
            vehicle_map[arac_str] = equipment.id
            print(f"  + Tramvay {arac_no} (Kod: TRN-{arac_no}, Km: {km})")
        
        db.session.commit()
        print(f"\n{len(vehicle_map)} tramvay eklendi")
        
        # Mevcut FRACAS arızalarını sil
        Failure.query.filter(Failure.failure_code.like('BOZ-%')).delete()
        db.session.commit()
        
        # Arıza kayıtlarını ekle
        print(f"\n=== ARIZA KAYITLARI ===")
        
        # Sütun isimlerini bul
        cols = {
            'fracas_id': 'FRACAS ID',
            'arac': arac_col,
            'modul': [c for c in df.columns if 'Module' in c][0],
            'tarih': [c for c in df.columns if 'Hata Tarih' in c][0],
            'saat': [c for c in df.columns if 'Hata Saat' in c][0],
            'konum': [c for c in df.columns if 'Arıza Konumu' in c][0],
            'tanim': [c for c in df.columns if 'Arıza Tanımı' in c][0],
            'sinif': [c for c in df.columns if 'Arıza Sınıfı' in c and 'DDU' not in c][0],
            'tip': [c for c in df.columns if 'Arıza Tipi' in c][0],
            'tedarikci': [c for c in df.columns if 'İlgili Tedarikçi' in c][0],
            'aksiyon': [c for c in df.columns if 'Aksiyon' in c and 'Tespitini' not in c][0],
            'garanti': [c for c in df.columns if 'Garanti' in c][0],
            'tamir_suresi': [c for c in df.columns if 'Tamir Süresi (dakika)' in c][0],
            'servis_tarih': [c for c in df.columns if 'Servise Veriliş Tarih' in c][0],
            'detay': [c for c in df.columns if 'Detaylı Bilgi' in c][0],
            'ncr': [c for c in df.columns if 'NCR Numarası' in c][0],
        }
        
        ariza_sayisi = 0
        acik_ariza = 0
        cozulen_ariza = 0
        
        for idx, row in df.iterrows():
            fracas_id = row[cols['fracas_id']]
            if pd.isna(fracas_id):
                continue
            
            arac_no = row[cols['arac']]
            equipment_id = vehicle_map.get(str(arac_no).strip()) if pd.notna(arac_no) else None
            
            # Tarih işleme
            tarih = row[cols['tarih']]
            failure_date = None
            if pd.notna(tarih):
                if isinstance(tarih, datetime):
                    failure_date = tarih
                else:
                    try:
                        failure_date = pd.to_datetime(tarih)
                    except:
                        pass
            
            # Çözüldü mü kontrol et
            servis_tarih = row[cols['servis_tarih']]
            is_resolved = pd.notna(servis_tarih)
            
            resolved_date = None
            if is_resolved and pd.notna(servis_tarih):
                if isinstance(servis_tarih, datetime):
                    resolved_date = servis_tarih
                else:
                    try:
                        resolved_date = pd.to_datetime(servis_tarih)
                    except:
                        pass
            
            # Severity belirleme
            sinif = str(row[cols['sinif']]) if pd.notna(row[cols['sinif']]) else ''
            if 'Kritik' in sinif or 'A' == sinif.strip():
                severity = 'kritik'
            elif 'Büyük' in sinif or 'B' in sinif:
                severity = 'yuksek'
            elif 'Küçük' in sinif or 'C' in sinif:
                severity = 'orta'
            else:
                severity = 'dusuk'
            
            # Tamir süresi
            tamir_suresi = row[cols['tamir_suresi']]
            downtime = int(tamir_suresi) if pd.notna(tamir_suresi) and tamir_suresi > 0 else 0
            
            # Status belirleme
            if is_resolved:
                status = 'cozuldu'
                cozulen_ariza += 1
            else:
                status = 'acik'
                acik_ariza += 1
            
            failure = Failure(
                failure_code=str(fracas_id),
                equipment_id=equipment_id,
                title=str(row[cols['tanim']])[:200] if pd.notna(row[cols['tanim']]) else f'Arıza {fracas_id}',
                description=str(row[cols['detay']]) if pd.notna(row[cols['detay']]) else '',
                severity=severity,
                failure_type=str(row[cols['tip']]) if pd.notna(row[cols['tip']]) else 'belirsiz',
                failure_mode=str(row[cols['konum']]) if pd.notna(row[cols['konum']]) else '',
                root_cause=str(row[cols['tedarikci']]) if pd.notna(row[cols['tedarikci']]) else '',
                status=status,
                failure_date=failure_date or datetime.now(),
                detected_date=failure_date or datetime.now(),
                resolved_date=resolved_date,
                downtime_minutes=downtime,
                resolution_notes=str(row[cols['aksiyon']]) if pd.notna(row[cols['aksiyon']]) else '',
                corrective_action=str(row[cols['aksiyon']]) if pd.notna(row[cols['aksiyon']]) else ''
            )
            db.session.add(failure)
            ariza_sayisi += 1
            
            # Her 10 kayıtta bir log
            if ariza_sayisi % 10 == 0:
                print(f"  ... {ariza_sayisi} arıza işlendi")
        
        db.session.commit()
        
        # Araç durumlarını güncelle (açık arızası olan araçlar)
        for arac_str, eq_id in vehicle_map.items():
            acik_ariza_var = Failure.query.filter_by(equipment_id=eq_id, status='acik').count() > 0
            equipment = Equipment.query.get(eq_id)
            if equipment:
                if acik_ariza_var:
                    equipment.status = 'ariza'
                else:
                    equipment.status = 'aktif'
        
        db.session.commit()
        
        print(f"\n=== ÖZET ===")
        print(f"Toplam Tramvay: {len(vehicle_map)}")
        print(f"Toplam Arıza: {ariza_sayisi}")
        print(f"  - Açık Arıza: {acik_ariza}")
        print(f"  - Çözülen Arıza: {cozulen_ariza}")
        print(f"\nVeritabanı başarıyla güncellendi!")


if __name__ == '__main__':
    sync_fracas_data()
