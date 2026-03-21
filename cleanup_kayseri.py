"""
Kayseri projesi veri güncellemesi - 4000+ araçları sil
"""
from app import app, db
from models import ServiceStatus

with app.app_context():
    # Adım 1: Kontrol
    print("ADIM 1: Yanlış araçları bul")
    print("-" * 60)
    
    bad_records = db.session.query(ServiceStatus).filter(
        ServiceStatus.project_code == 'kayseri'
    ).all()
    
    print(f"Kayseri'nin tüm ServiceStatus kayıtları: {len(bad_records)}")
    
    # Araç listesini al
    trams = set()
    for rec in bad_records:
        trams.add(rec.tram_id)
    
    trams_sorted = sorted(list(trams))
    print(f"Kayseri araçları: {trams_sorted}")
    
    # Adım 2: 4000+ olanları belirle
    print("\nADIM 2: 4000+ araçları bul ve sil")
    print("-" * 60)
    
    bad_trams = [t for t in trams_sorted if int(t) >= 4000]
    print(f"Silinecek araçlar: {bad_trams}")
    
    if bad_trams:
        # Sil
        deleted = db.session.query(ServiceStatus).filter(
            ServiceStatus.project_code == 'kayseri',
            ServiceStatus.tram_id.in_(bad_trams)
        ).delete(synchronize_session=False)
        
        db.session.commit()
        print(f"✓ {deleted} kayıt silindi")
    else:
        print("Silinecek kayıt bulunamadı")
    
    # Adım 3: Doğrulama
    print("\nADIM 3: Doğrulama")
    print("-" * 60)
    
    remaining = db.session.query(ServiceStatus).filter(
        ServiceStatus.project_code == 'kayseri'
    ).all()
    
    final_trams = set()
    for rec in remaining:
        final_trams.add(rec.tram_id)
    
    final_trams_sorted = sorted(list(final_trams))
    print(f"Güncellenmiş araçlar: {final_trams_sorted}")
    print(f"Toplam kayıt: {len(remaining)}")
    
    if final_trams_sorted == ['3872', '3873', '3874', '3875', '3876', '3877', '3878', '3879', '3880', '3881', '3882']:
        print("\n✅ BAŞARILI: Kayseri veri tabanı düzeltildi!")
    else:
        print(f"\n⚠️ UYARI: Beklenmedik sonuç")
