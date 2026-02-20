from app import create_app, db, ServiceStatus

app = create_app()

with app.app_context():
    # Eski verileri bul
    records = ServiceStatus.query.filter(ServiceStatus.aciklama.ilike('%Dünden kopyalandı%')).all()
    print(f'Eski veriler bulundu: {len(records)} kayıt\n')

    if records:
        for r in records[:10]:
            print(f'{r.tram_id} - {r.date}: {r.aciklama}')
        
        # Eski yazı ile birlikte kaydedilenleri güncelle
        print(f'\nTemizleniyor...')
        for record in records:
            record.aciklama = record.aciklama.replace(' (Dünden kopyalandı)', '').strip()
        
        db.session.commit()
        print(f'{len(records)} kayıt temizlendi!')
    else:
        print('Eski veri bulunamadı.')
