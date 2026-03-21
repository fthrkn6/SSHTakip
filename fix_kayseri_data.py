#!/usr/bin/env python3
"""
Kayseri projesi için yanlış araç verilerini temizle
- ServiceStatus'tan 4001-4022 araçlarını sil
"""

from app import app
from models import db, ServiceStatus

def fix_kayseri_data():
    with app.app_context():
        print("=" * 60)
        print("Kayseri projesi veri temizleme başladı...")
        print("=" * 60)
        
        # Kayseri projesi için 4001-4022 araçlarını sil
        bad_records = db.session.query(ServiceStatus).filter(
            ServiceStatus.project_code == 'kayseri',
            ServiceStatus.tram_id.in_([str(i) for i in range(4001, 4023)])
        ).all()
        
        print(f'\n❌ Silinecek yanlış kaydı bulundu: {len(bad_records)}')
        
        # Sil
        for record in bad_records:
            db.session.delete(record)
        
        db.session.commit()
        print('✓ Yanlış veriler silindi\n')
        
        # Kontrol et
        kayseri_statuses = db.session.query(ServiceStatus.tram_id).filter_by(
            project_code='kayseri'
        ).distinct().all()
        
        trams = sorted([s[0] for s in kayseri_statuses])
        print('Kayseri ServiceStatus doğru araçlar:')
        print(f'  {trams}')
        
        # Aralık kontrol et
        tram_ints = [int(t) for t in trams]
        expected_min = 3872
        expected_max = 3882
        actual_min = min(tram_ints)
        actual_max = max(tram_ints)
        
        if actual_min == expected_min and actual_max == expected_max and len(trams) == 11:
            print(f'\n✅ BAŞARILI: Kayseri araçları doğru (3872-3882)')
        else:
            print(f'\n⚠️  UYARI: Beklenmeyen sonuç')
            print(f'   Beklenen: 3872-3882 (11 araç)')
            print(f'   Gerçek: {actual_min}-{actual_max} ({len(trams)} araç)')

if __name__ == '__main__':
    fix_kayseri_data()
