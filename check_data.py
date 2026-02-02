"""Veritabanı kontrolü"""
import sys
sys.path.insert(0, '.')

from app import app, db
from models import Equipment, Failure

with app.app_context():
    print("=" * 60)
    print("TRAMVAY FİLOSU")
    print("=" * 60)
    
    tramvaylar = Equipment.query.filter_by(equipment_type='Tramvay').all()
    for t in tramvaylar:
        ariza_sayisi = Failure.query.filter_by(equipment_id=t.id).count()
        acik_ariza = Failure.query.filter_by(equipment_id=t.id).filter(
            Failure.status.in_(['acik', 'devam_ediyor'])
        ).count()
        print(f"  {t.equipment_code}: {t.name}")
        print(f"    Durum: {t.status} | KM: {t.total_km}")
        print(f"    Toplam Arıza: {ariza_sayisi} | Açık: {acik_ariza}")
        print()
    
    print("=" * 60)
    print("AÇIK ARIZALAR")
    print("=" * 60)
    
    acik_arizalar = Failure.query.filter(
        Failure.status.in_(['acik', 'devam_ediyor'])
    ).all()
    
    for a in acik_arizalar:
        arac = a.equipment.name if a.equipment else "Bilinmiyor"
        print(f"  [{a.failure_code}] {a.title[:60]}")
        print(f"    Araç: {arac} | Şiddet: {a.severity} | Tarih: {a.failure_date}")
        print()
    
    print("=" * 60)
    print("ÇÖZÜLEN ARIZALAR (Son 5)")
    print("=" * 60)
    
    cozulen = Failure.query.filter_by(status='cozuldu').order_by(
        Failure.resolved_date.desc()
    ).limit(5).all()
    
    for a in cozulen:
        arac = a.equipment.name if a.equipment else "Bilinmiyor"
        print(f"  [{a.failure_code}] {a.title[:60]}")
        print(f"    Araç: {arac} | Çözüm: {a.resolved_date} | Süre: {a.downtime_minutes} dk")
        print()
    
    print("=" * 60)
    print("İSTATİSTİKLER")
    print("=" * 60)
    toplam_tramvay = Equipment.query.filter_by(equipment_type='Tramvay').count()
    toplam_ariza = Failure.query.filter(Failure.failure_code.like('BOZ-%')).count()
    acik_ariza_say = Failure.query.filter(
        Failure.failure_code.like('BOZ-%'),
        Failure.status.in_(['acik', 'devam_ediyor'])
    ).count()
    cozulen_say = Failure.query.filter(
        Failure.failure_code.like('BOZ-%'),
        Failure.status == 'cozuldu'
    ).count()
    
    print(f"  Toplam Tramvay: {toplam_tramvay}")
    print(f"  Toplam Arıza: {toplam_ariza}")
    print(f"  Açık Arıza: {acik_ariza_say}")
    print(f"  Çözülen Arıza: {cozulen_say}")
