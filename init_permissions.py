"""
İzin (Permission) ve Rol İzin (RolePermission) tablolarına başlangıç verileri yükle
"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Permission, RolePermission, User

def init_permissions():
    """Başlangıç izinlerini ve rol izinlerini ekle"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*100)
        print("İzin (Permission) Başlangıç Verileri Yükleme")
        print("="*100 + "\n")
        
        # Sistem sayfaları ve işlemleri tanımla
        permissions_data = [
            # Dashboard ve Raporlar
            {
                'page_name': 'dashboard',
                'display_name': 'Gösterge Paneli',
                'url': '/dashboard',
                'description': 'Ana gösterge panelini görüntüle'
            },
            {
                'page_name': 'raporlar',
                'display_name': 'Raporlar',
                'url': '/reports',
                'description': 'Sistem raporlarını görüntüle'
            },
            
            # Ekipman Yönetimi
            {
                'page_name': 'ekipman',
                'display_name': 'Ekipman Listesi',
                'url': '/ekipman',
                'description': 'Ekipman bilgilerini görüntüle'
            },
            {
                'page_name': 'ekipman_ekle',
                'display_name': 'Ekipman Ekle',
                'url': '/ekipman/ekle',
                'description': 'Yeni ekipman ekle'
            },
            
            # Arıza Yönetimi
            {
                'page_name': 'ariza_listesi',
                'display_name': 'Arıza Listesi',
                'url': '/ariza-listesi',
                'description': 'Arıza kayıtlarını görüntüle'
            },
            {
                'page_name': 'ariza_ekle',
                'display_name': 'Arıza Raporu Oluştur',
                'url': '/ariza/ekle',
                'description': 'Yeni arıza raporu oluştur'
            },
            
            # Bakım Planlaması
            {
                'page_name': 'bakim_plani',
                'display_name': 'Bakım Planı',
                'url': '/bakim-plani',
                'description': 'Bakım planlarını görüntüle'
            },
            {
                'page_name': 'bakim_plani_ekle',
                'display_name': 'Bakım Planı Oluştur',
                'url': '/bakim-plani/ekle',
                'description': 'Yeni bakım planı oluştur'
            },
            
            # İş Emirleri
            {
                'page_name': 'is_emirleri',
                'display_name': 'İş Emirleri',
                'url': '/is-emirleri',
                'description': 'İş emirlerini görüntüle'
            },
            {
                'page_name': 'is_emri_ekle',
                'display_name': 'İş Emri Oluştur',
                'url': '/is-emri/ekle',
                'description': 'Yeni iş emri oluştur'
            },
            
            # Yönetim Panelleri
            {
                'page_name': 'kullanicilar',
                'display_name': 'Kullanıcı Yönetimi',
                'url': '/kullanicilar',
                'description': 'Sistemdeki kullanıcıları yönet'
            },
            {
                'page_name': 'yetkilendirme',
                'display_name': 'Yetki Yönetimi',
                'url': '/admin/yetkilendirme',
                'description': 'Rol ve sayfa izinlerini yönet'
            },
            {
                'page_name': 'projeler',
                'display_name': 'Proje Yönetimi',
                'url': '/projeler',
                'description': 'Projeleri yönet'
            },
            
            # Yapılandırma
            {
                'page_name': 'ayarlar',
                'display_name': 'Sistem Ayarları',
                'url': '/settings',
                'description': 'Sistem ayarlarını yapılandır'
            },
            {
                'page_name': 'yedekleme',
                'display_name': 'Yedekleme ve Geri Yükleme',
                'url': '/yedekleme',
                'description': 'Veritabanı yedekleme ve geri yükleme'
            }
        ]
        
        # Permission'ları ekle (varsa atla)
        print("1. İzinler ekleniyor...\n")
        permissions = {}
        
        for perm_data in permissions_data:
            existing = Permission.query.filter_by(page_name=perm_data['page_name']).first()
            
            if not existing:
                perm = Permission(**perm_data)
                db.session.add(perm)
                print(f"   ✓ Eklendi: {perm_data['display_name']} ({perm_data['page_name']})")
            else:
                print(f"   - Zaten var: {perm_data['display_name']} (ID: {existing.id})")
            
            permissions[perm_data['page_name']] = existing.id if existing else None
        
        db.session.commit()
        
        # Yeniden yükle (yeni ID'ler almak için)
        print("\n2. İzinler kaydediliyor...\n")
        permissions = {}
        for perm_data in permissions_data:
            perm = Permission.query.filter_by(page_name=perm_data['page_name']).first()
            if perm:
                permissions[perm_data['page_name']] = perm.id
        
        # Rol İzinlerini Tanımla
        print("3. Rol izinleri atanıyor...\n")
        
        role_permissions = {
            'admin': [
                # Admin'in tüm izinleri var
                perm for perm in permissions.values() if perm
            ],
            'manager': [
                # Manager: Dashboard, Rapor, Ekipman, Arıza, Bakım, İş emirleri, Kullanıcılar
                permissions.get('dashboard'),
                permissions.get('raporlar'),
                permissions.get('ekipman'),
                permissions.get('ariza_listesi'),
                permissions.get('ariza_ekle'),
                permissions.get('bakim_plani'),
                permissions.get('bakim_plani_ekle'),
                permissions.get('is_emirleri'),
                permissions.get('is_emri_ekle'),
                permissions.get('kullanicilar'),
            ],
            'saha': [
                # Saha: Dashboard, Ekipman, Arıza, Bakım, İş emirleri
                permissions.get('dashboard'),
                permissions.get('ekipman'),
                permissions.get('ariza_listesi'),
                permissions.get('ariza_ekle'),
                permissions.get('bakim_plani'),
                permissions.get('is_emirleri'),
            ]
        }
        
        # RolePermission tablosunu temizle ve yeniden doldur
        RolePermission.query.delete()
        
        for role, perm_ids in role_permissions.items():
            for perm_id in perm_ids:
                if perm_id:
                    role_perm = RolePermission(role=role, permission_id=perm_id)
                    db.session.add(role_perm)
                    perm_name = Permission.query.get(perm_id).page_name
                    print(f"   ✓ {role.upper()}: {perm_name}")
        
        db.session.commit()
        
        print("\n" + "="*100)
        print("✓ İzin yönetimi başlangıç verileri başarıyla yüklendi!")
        print("="*100 + "\n")
        
        # Özet
        print("ÖZET:")
        print(f"  · Tanımlanan İzin Sayısı: {Permission.query.count()}")
        print(f"  · Atanan Rol İzin Sayısı: {RolePermission.query.count()}")
        print(f"  · Admin İzinleri: {RolePermission.query.filter_by(role='admin').count()}")
        print(f"  · Manager İzinleri: {RolePermission.query.filter_by(role='manager').count()}")
        print(f"  · Saha İzinleri: {RolePermission.query.filter_by(role='saha').count()}\n")

if __name__ == '__main__':
    init_permissions()
