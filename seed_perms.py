"""Simple permission seeder"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from models import Permission, RolePermission

app = create_app()
with app.app_context():
    # Create tables
    db.create_all()
    logger.info(f"\2")
    
    # Clear old permissions
    Permission.query.delete()
    RolePermission.query.delete()
    db.session.commit()
    logger.info(f"\2")
    
    # Add new permissions
    perms = [
        ('dashboard', 'Gösterge Paneli'),
        ('ariza_listesi', 'Arıza Listesi'),
        ('bakim_plani', 'Bakım Planları'),
        ('yedek_parca', 'Yedek Parça'),
        ('fracas', 'FRACAS Analiz'),
        ('kpi', 'KPI Dashboard'),
        ('kullanicilar', 'Kullanıcı Yönetimi'),
        ('yetkilendirme', 'Yetki Yönetimi'),
        ('admin_panel', 'Admin Paneli'),
    ]
    
    for page_name, display_name in perms:
        p = Permission(page_name=page_name, display_name=display_name)
        db.session.add(p)
    
    db.session.commit()
    logger.info(f"\2")
    
    # Get permission IDs
    perm_dict = {}
    for page_name, _ in perms:
        p = Permission.query.filter_by(page_name=page_name).first()
        if p:
            perm_dict[page_name] = p.id
    
    logger.info(f"\2")
    
    # Add role permissions
    role_perms = {
        'admin': list(perm_dict.values()),
        'manager': [
            perm_dict.get('dashboard'),
            perm_dict.get('ariza_listesi'),
            perm_dict.get('bakim_plani'),
            perm_dict.get('fracas'),
            perm_dict.get('kpi'),
            perm_dict.get('kullanicilar'),
        ],
        'saha': [
            perm_dict.get('dashboard'),
            perm_dict.get('ariza_listesi'),
            perm_dict.get('bakim_plani'),
        ]
    }
    
    for role, perm_ids in role_perms.items():
        for perm_id in perm_ids:
            if perm_id:
                rp = RolePermission(role=role, permission_id=perm_id)
                db.session.add(rp)
    
    db.session.commit()
    
    # Count
    rp_count = RolePermission.query.count()
    p_count = Permission.query.count()
    
    logger.info(f"\2")
    logger.info(f"\2")
    logger.info("\1")
