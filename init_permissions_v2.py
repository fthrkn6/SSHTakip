"""
İzin (Permission) ve Rol İzin (RolePermission) tablolarına başlangıç verileri yükle
"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Permission, RolePermission

def init_permissions():
    """Başlangıç izinlerini ve rol izinlerini ekle"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*100)
        print("İzin (Permission) Başlangıç Verileri Yükleme")
        print("="*100 + "\n")
        sys.stdout.flush()
        
        # Sistem sayfaları ve işlemleri tanımla
        permissions_data = [
            ('dashboard', 'Gösterge Paneli', '/dashboard'),
            ('ariza_listesi', 'Arıza Listesi', '/ariza-listesi'),
            ('bakim_plani', 'Bakım Planları', '/bakim-plani'),
            ('yedek_parca', 'Yedek Parça', '/yedek-parca'),
            ('fracas', 'FRACAS Analiz', '/fracas'),
            ('kpi', 'KPI Dashboard', '/kpi'),
            ('kullanicilar', 'Kullanıcı Yönetimi', '/kullanicilar'),
            ('yetkilendirme', 'Yetki Yönetimi', '/admin/yetkilendirme'),
            ('admin_panel', 'Admin Paneli', '/admin'),
        ]
        
        # Permission'ları ekle
        print("1. Tablolar oluşturuluyor...")
        sys.stdout.flush()
        db.create_all()
        print("   ✓ Tablolar oluşturuldu\n")
        sys.stdout.flush()
        
        print("2. İzinler ekleniyor...\n")
        sys.stdout.flush()
        
        # Mevcut Permission'ları sil
        Permission.query.delete()
        
        permissions = {}
        for page_name, display_name, url in permissions_data:
            perm = Permission(page_name=page_name, display_name=display_name, url=url)
            db.session.add(perm)
            print(f"   ✓ {display_name}")
            sys.stdout.flush()
        
        db.session.commit()
        
        # Permission ID'lerini al
        print("\n3. İzin ID'leri alınıyor...\n")
        sys.stdout.flush()
        permissions = {}
        for perm_data in permissions_data:
            perm = Permission.query.filter_by(page_name=perm_data[0]).first()
            if perm:
                permissions[perm_data[0]] = perm.id
        
        # Rol İzinlerini Tanımla
        print("4. Rol izinleri atanıyor...\n")
        sys.stdout.flush()
        
        role_permissions = {
            'admin': list(permissions.values()),  # Tüm izinler
            'manager': [
                permissions.get('dashboard'),
                permissions.get('ariza_listesi'),
                permissions.get('bakim_plani'),
                permissions.get('fracas'),
                permissions.get('kpi'),
                permissions.get('kullanicilar'),
            ],
            'saha': [
                permissions.get('dashboard'),
                permissions.get('ariza_listesi'),
                permissions.get('bakim_plani'),
            ]
        }
        
        # RolePermission'ları ekle
        RolePermission.query.delete()
        
        for role, perm_ids in role_permissions.items():
            count = 0
            for perm_id in perm_ids:
                if perm_id:
                    rp = RolePermission(role=role, permission_id=perm_id)
                    db.session.add(rp)
                    count += 1
            print(f"   ✓ {role.upper()}: {count} izin")
            sys.stdout.flush()
        
        db.session.commit()
        
        print("\n" + "="*100)
        print("✓ İzin yönetimi başlangıç verileri başarıyla yüklendi!")
        print("="*100 + "\n")
        sys.stdout.flush()
        
        # Özet
        perm_count = Permission.query.count()
        rp_count = RolePermission.query.count()
        
        print("ÖZET:")
        print(f"  · Tanımlanan İzin Sayısı: {perm_count}")
        print(f"  · Toplam Rol İzin Sayısı: {rp_count}")
        print(f"  · Admin İzinleri: {RolePermission.query.filter_by(role='admin').count()}")
        print(f"  · Manager İzinleri: {RolePermission.query.filter_by(role='manager').count()}")
        print(f"  · Saha İzinleri: {RolePermission.query.filter_by(role='saha').count()}\n")
        sys.stdout.flush()

if __name__ == '__main__':
    init_permissions()
