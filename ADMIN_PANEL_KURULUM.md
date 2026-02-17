# SSH Takip - Rol Sistemi & Admin Panel Kurulum Rehberi

## 📋 GENEL BAKIŞ

Bu rehber, SSH Takip sistemine entegre edilen **rol tabanlı erişim kontrolü (RBAC)** ve **admin panelinin** kurulumunu ve kullanımını açıklar.

---

## 🎯 SISTEM ÖZELLİKLERİ

### Rol Türleri

1. **Admin (Yönetici)** 🔐
   - Tüm projelere erişim
   - Sistem yönetimi (Kullanıcı/Proje/Yedek)
   - Admin paneline tam erişim
   - Diğer kullanıcıları yönetebilir

2. **Saha (Alan Çalışanı)** 🔧
   - Sadece atanan projelere erişim
   - Arıza bildirimi
   - Bakım yönetimi
   - Raporlar (atanan projeler için)

### Proje İzolasyonu
- Her proje kendine ait veri klasörüne sahiptir: `logs/{project_code}/`
- Kullanıcılar sadece atanan projelerin verilerine erişebilirler
- Admin tüm projeleri görebilir ve yönetebilir

### Otomatik Yedekleme
- Her form gönderiminde otomatik yedek yapılır
- Yedekler `logs/{project}/archive/` klasöründe saklanır
- Geri yükleme ve yedek geçmişi admin panelden yönetilir

---

## 🚀 KURULUM ADIMLARI

### 1. Veritabanını Hazırla

```bash
# Database'i initialize et (ilk kez çalıştırırsa)
python
>>> from app import create_app
>>> from models import db
>>> app = create_app()
>>> app.app_context().push()
>>> db.create_all()
>>> exit()
```

### 2. İlk Admin Kullanıcısını Oluştur

```bash
python setup_admin_user.py
```

Ekranda açılacak menüde **1. seçeneği** seçerek ilk admin kullanıcısını oluşturun.

**Varsayılan Admin Kredileri:**
- Username: `admin`
- Password: `Admin123!`
- Email: `admin@bozankaya.com`

⚠️ **ÖNEMLİ:** İlk login'den sonra şifreyi değiştirin!

### 3. Saha Kullanıcıları Oluştur (Opsiyonel)

```bash
python setup_admin_user.py
```

Menüde **2. seçeneği** seçerek demo saha kullanıcıları oluşturun.

Veya **Admin Panel** → **Kullanıcı Yönetimi** → **Yeni Kullanıcı** ile manuel olarak oluşturun.

### 4. Uygulamayı Başlat

```bash
python run.py
```

Uygulama `http://localhost:5000` adresinde çalışmaya başlayacak.

---

## 🔐 LOGIN VE KULLANICI AKIŞI

### 1. System'e Giriş

1. `http://localhost:5000/login` adresine gidin
2. Admin kredileriyle giriş yapın

### 2. Proje Seçimi (Navbar'da)

- **Admin Kullanıcı:** Tüm projeler görüntülenir
- **Saha Kullanıcı:** Sadece atanan projeler görüntülenir
- Proje seçiciden farklı projeye geçebilirsiniz

### 3. Admin Paneline Erişim

Navbar'da sağ üst köşede ⚙️ **Admin Panel** butonu
↓
`/admin/dashboard` adresine yönlendirilirsiniz

---

## 👨‍💼 ADMIN PANEL - ÖZELLÎKLER

### Dashboard (`/admin/dashboard`)

İstatistikler:
- Toplam Kullanıcı Sayısı
- Admin / Saha Kullanıcı Dağılımı
- Aktif Proje Sayısı
- Son Yedekleme Tarihleri
- Son Giriş Yapanlar

Hızlı İşlemler:
- Kullanıcı Yönetimi
- Proje Yönetimi
- Yedekleme Yönetimi

### Kullanıcı Yönetimi (`/admin/users`)

**Listeleme:**
- Tüm sistem kullanıcıları
- Kullanıcı rolü ve atanan projeler
- Son giriş zamanı

**Yeni Kullanıcı Ekle (`/admin/users/add`):**
- Kullanıcı adı, email, ad soyadı
- Rol seçimi (Admin / Saha)
- Saha kullanıcısı için proje atama

**Kullanıcı Düzenle (`/admin/users/<id>/edit`):**
- Tüm bilgileri güncelle
- Şifreyi değiştir
- Rol değiştir
- Proje atamalarını değiştir

**Kullanıcı Sil (`/admin/users/<id>/delete`):**
- Sistem'den kullanıcıyı kaldır
- Kendi hesabınızı silemezsiniz

### Proje Yönetimi (`/admin/projects`)

**Proje Listeleme:**
- Tüm projeler ve detayları
- Proje durumu (aktif/arşiv)
- Veri dosyaları kontrolü
- Yedek sayısı

**Yeni Proje Ekle (`/admin/projects/add`):**
- Proje kodu (unique)
- Proje adı
- Açıklama
- Konum
- İletişim bilgileri (opsiyonel)

Otomatik olarak klasör yapısı oluşturulur:
```
logs/{project_code}/
├── veriler/              (reference data)
├── ariza_listesi/        (failure records)
├── config/               (project config)
└── archive/              (timestamped backups)
```

**Proje Arşivle:**
- Projeyi silinmeden arşivleme (soft delete)
- Veri korunur, yeni veri eklenemez

### Yedekleme Yönetimi (`/admin/backups`)

**Yedek Listesi:**
- Her proje için yedek geçmişi
- Tarih ve boyut bilgisi
- Son yedekleme tarihi

**Manuel Yedekleme:**
- Belirli proje için yedek oluştur
- "Tüm Projeleri Yedekle" butonu

**Yedek Bilgileri:**
- Otomatik yedekleme: Form gönderiminde
- Saklama süresi: 30 gün
- Konum: `logs/{project}/archive/`

---

## 🛡️ ROL TABANI ERİŞİM KONTROLÜ

### İmplementasyon

**Dekoratörler** (`utils/auth_decorators.py`):

```python
from utils.auth_decorators import (
    require_admin,
    require_project_access,
    require_saha_role
)

# Sadece admin
@app.route('/admin/users')
@login_required
@require_admin
def admin_users():
    ...

# Proje erişim kontrolü
@app.route('/project/<project_code>/dashboard')
@login_required
@require_project_access('project_code')
def project_dashboard(project_code):
    ...
```

### User Model Methods

```python
user = User.query.get(1)

# Rol kontrolü
user.is_admin()                      # bool
user.is_saha()                       # bool

# Proje kontrolü
user.can_access_project('belgrad')   # bool

# Atanan projeler
user.get_assigned_projects()         # ['belgrad', 'ankara'] or '*'

# Rol adı (Türkçe)
user.get_role_display()              # 'Yönetici' | 'Saha Kullanıcısı'
```

### Session Yönetimi

Login sonrasında, `before_request` hook'u:
1. Query parameter'dan proje kodunu kontrol eder: `?project=belgrad`
2. Kullanıcının o projeye erişim yetkisini kontrol eder
3. `session['project_code']` set eder
4. Navbar'da gösterir

---

## 🔄 OTOMATIK YEDEKLEME AKIŞI

### Form Gönderimi

1. **Yeni Arıza Bildir** formunu doldurup gönder
2. ✅ Arıza Listesi Excel'e yazılır
3. 💾 **Otomatik yedek oluşturulur**: `logs/{project}/archive/YYYYMMDD-HHMMSS.xlsx`
4. ✅ Fracas template'ine yazılır
5. 💾 **Otomatik yedek oluşturulur**
6. ✅ Sayfada başarı mesajı gösterilir

### Yedek Dosya Konumu

```
logs/belgrad/archive/
├── 20260217-224230_Ariza_Listesi_belgrad.xlsx
├── 20260217-215015_Fracas_BELGRAD.xlsx
├── 20260217-210845_Ariza_Listesi_belgrad.xlsx
└── ...
```

### Yedekleri Yönetme

**Admin Panel** → **Yedekleme** → 
- Geçmiş yedekleri görüntüle
- Manuel yedek oluştur
- Tüm projeleri yedekle

---

## 📊 PROJE PARAMETRIZASYONU

Çoğu route artık proje parametresi alır:

```python
# Dashboard
get_tram_ids_from_veriler(project_code='belgrad')
get_failures_from_excel(project_code='belgrad')

# FRACAS
load_fracas_data(project_code='belgrad')

# ProjectManager ile dosya yolları
ProjectManager.get_veriler_file('belgrad')
ProjectManager.get_fracas_file('belgrad')
```

Session'dan proje alınırsa:
```python
project_code = session.get('current_project', 'belgrad')
```

---

## 🧪 TEST ÇALIŞTIRILMESI

```bash
python test_admin_system.py
```

Testler:
1. ✓ User Model (isAdmin, isSaha, canAccessProject)
2. ✓ Admin Routes (12 route eşlemesi)
3. ✓ Decorators (@require_admin, @require_project_access)
4. ✓ Templates (7 admin template dosyası)
5. ✓ Imports (Kritik modüller)

---

## ❌ TROUBLESHOOT

### "Admin Panel'e erişim yetkim yok"

**Çözüm:** Kullanıcınızın role'ü 'admin' mı kontrol edin
```python
python
>>> from models import User
>>> user = User.query.filter_by(username='your_username').first()
>>> print(user.role)
>>> user.role = 'admin'
>>> db.session.commit()
```

### "Projeyi göremiyorum"

**Çözüm:** Atanan projeler kontrol edin
```python
>>> user.get_assigned_projects()
>>> user.set_assigned_projects(['belgrad', 'ankara'])
>>> db.session.commit()
```

### "Yedek oluşturamıyorum"

**Çözüm:** Klasörleri kontrol edin
```bash
mkdir -p logs/belgrad/archive
chmod 777 logs/belgrad/archive
```

### Session'da proje kodu görünmüyor

**Çözüm:** Navbar'da proje seç veya:
```python
# URL'ye ekle
http://localhost:5000/dashboard?project=belgrad
```

---

## 📝 NOTLAR & BESTPRACTİCES

1. **Şifre Yönetimi:**
   - Admin ilk login'den sonra şifresini değiştirsin
   - Güçlü şifreler kullanın (8+ karakter, numara, özel karakter)

2. **Proje Yönetimi:**
   - Proje kodunu oluşturduktan sonra değiştiremezsiniz
   - Soft delete (arşivle) kullanın, hard delete'i dikkatli yapın

3. **Yedekleme:**
   - 30 günlük eski yedekleri sistem otomatik siler
   - Önemli yedekleri (`archive/` dışına)manuel backup alın

4. **Kullanıcı Yönetimi:**
   - Minimum ayrıcalık ilkesi (principle of least privilege)
   - Admin'i sadece ihtiyaç sahiplerine verin
   - Saıl kullanıcıları sadece ihtiyaç duyduğu projelere atayın

5. **Denetim:**
   - Admin Panel → Sistem Logları (yönk açılacak)
   - Tüm kritik işlemler log'lanmalıdır

---

## 🔗 İLGİLİ DOSYALAR

| Dosya | Amaç |
|-------|------|
| `models.py` | User model (role, assigned_projects) |
| `routes/admin.py` | Admin panel route'ları |
| `utils/auth_decorators.py` | Rol kontrol dekoratörleri |
| `utils/project_manager.py` | Proje yönetimi ve path resolution |
| `utils/backup_manager.py` | Yedekleme ve geri yükleme |
| `templates/admin/` | Admin panel şablonları |
| `templates/base.html` | Navbar (proje seçici) |
| `test_admin_system.py` | Test suite |
| `setup_admin_user.py` | Admin user setup script |

---

## 📞 DESTEK

Sorunlar için:
1. Logs kontrol edin: `logs/`
2. Database'i kontrol edin: `ssh_takip_bozankaya.db`
3. Test çalıştırın: `python test_admin_system.py`
4. Geçmiş commit'leri kontrol edin: `git log admin`

---

**Son Güncelleme:** 2026-02-17  
**Versiyon:** 1.0.0 (Admin Panel Release)
