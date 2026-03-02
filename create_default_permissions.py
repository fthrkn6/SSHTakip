"""
Default izinleri oluştur - Admin Paneli Sayfaları ve Proje Yönetimi
"""
from app import create_app
from models import db, Permission, Role

app = create_app()

with app.app_context():
    # Sayfa İzinleri
    page_permissions = [
        ('dashboard', 'Dashboard - Ana Gösterge Paneli', 'page'),
        ('users', 'Kullanıcı Yönetimi', 'page'),
        ('projects', 'Proje Yönetimi', 'page'),
        ('equipment', 'Ekipman Yönetimi', 'page'),
        ('maintenance', 'Bakım Planlaması', 'page'),
        ('reports', 'Raporlar & Analiz', 'page'),
        ('services', 'Servis Yönetimi', 'page'),
        ('compliance', 'Uyum & Denetim', 'page'),
        ('settings', 'Sistem Ayarları', 'page'),
    ]
    
    # Proje İzinleri
    project_permissions = [
        ('belgrad', 'Belgrad Projesi', 'project'),
        ('ankara', 'Ankara Projesi', 'project'),
        ('izmir', 'İzmir Projesi', 'project'),
    ]
    
    # Mevcut izinleri sil ve yeniden oluştur
    Permission.query.delete()
    db.session.commit()
    
    created_count = 0
    
    # Sayfa izinlerini ekle
    for name, desc, category in page_permissions:
        if not Permission.query.filter_by(name=name).first():
            perm = Permission(name=name, description=desc, category=category)
            db.session.add(perm)
            created_count += 1
    
    # Proje izinlerini ekle
    for name, desc, category in project_permissions:
        if not Permission.query.filter_by(name=name).first():
            perm = Permission(name=name, description=desc, category=category)
            db.session.add(perm)
            created_count += 1
    
    db.session.commit()
    
    print(f"✓ {created_count} izin oluşturuldu")
    
    # Rollere varsayılan izinleri ata
    admin_role = Role.query.filter_by(name='Admin').first()
    muhendis_role = Role.query.filter_by(name='Mühendis').first()
    teknisyen_role = Role.query.filter_by(name='Teknisyen').first()
    
    # Admin - Tüm izinler
    if admin_role:
        admin_role.permissions = Permission.query.all()
        print(f"✓ Admin: Tüm izinler {len(admin_role.permissions)} izin)")
    
    # Mühendis - Dashboard, Maintenance, Reports
    if muhendis_role:
        muhendis_role.permissions = Permission.query.filter(
            Permission.name.in_(['dashboard', 'maintenance', 'reports', 'projects', 'equipment'])
        ).all()
        print(f"✓ Mühendis: {len(muhendis_role.permissions)} izin")
    
    # Teknisyen - Dashboard, Equipment, Services
    if teknisyen_role:
        teknisyen_role.permissions = Permission.query.filter(
            Permission.name.in_(['dashboard', 'equipment', 'services'])
        ).all()
        print(f"✓ Teknisyen: {len(teknisyen_role.permissions)} izin")
    
    db.session.commit()
    print("\n✓ Default izinler başarıyla oluşturuldu!")
