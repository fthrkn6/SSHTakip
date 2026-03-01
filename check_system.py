from pathlib import Path
from app import PROJECTS, PAGES

base_dir = Path('.')
data_dir = base_dir / 'data'

print('=' * 80)
print('SSH TAKIP SISTEMI - SISTEM ANALIZI')
print('=' * 80)
print()

print(">> 1. PROJELER VE DOSYALAR")
print("-" * 80)

missing = []
for project in PROJECTS:
    code = project['code']
    name = project['name']
    p_dir = data_dir / code
    
    print(f'\n[{code.upper()}] {name} ({project.get("country", "?")})')
    print(f'     Path: {p_dir}')
    
    files = [
        f'{code.upper()} ANAHTARLAR LISTESI.XLSX',
        f'{code.upper()} GUNLUK RAPOR.XLSX',
        'Veriler.xlsx',
        'Parca Verileri.xlsx',
        'HBR LISTESI.XLSX',
        'Bakim Onleyici.XLSX',
    ]
    
    for f in files:
        fp = p_dir / f
        status = '[OK]' if fp.exists() else '[X]'
        print(f'     {status} {f}')
        if not fp.exists():
            missing.append((name, f))

if missing:
    print()
    print(">> EKSIK DOSYALAR TABLOSU")
    print("-" * 80)
    for prj, fname in missing:
        print(f'{prj:<15} : {fname}')
    print(f'Toplam: {len(missing)} dosya eksik')
else:
    print()
    print("[OK] Tum projeler icin gerekli dosyalar mevcut!")

print()
print(">> 2. UYGULAMANIN OZELLIKLERI")
print("-" * 80)
features = [
    'Dashboard (Genel ozet)',
    'Ariza Yonetimi (Bildirme, liste, HBR)',
    'Bakim Planlamasi (Planlar ve takvim)',
    'KM Takip (Kilometre takibi)',
    'Servis Durumu (Aktif durumlar)',
    'Yedek Parca (Envanter)',
    'FRACAS Analizi (Ariza analizi) [FILTER VE PDF GEREKLI]',
    'KPI Dashboard (Performans) [FILTER VE PDF GEREKLI]',
    'Senaryo Analizi (Simulasyonlar)',
    'Raporlar (Cesitli raporlar)',
    'Sistem Loglari (Audit)',
    'Dokumantasyon (Teknik dokulmanlar)',
    'Admin Panel (Kullanici yonetimi)',
    'Yetkilendirme (Rol tabanlı erisim)',
]

for i, feat in enumerate(features, 1):
    print(f'{i:2}. {feat}')

print()
print(">> 3. SAYFALAR VE IZIN YAPISI")
print("-" * 80)
by_section = {}
for page in PAGES:
    section = page.get('section', 'Diger')
    if section not in by_section:
        by_section[section] = []
    by_section[section].append(page)

total = 0
for section in sorted(by_section.keys()):
    pages = by_section[section]
    total += len(pages)
    print(f'\n{section}: ({len(pages)} sayfa)')
    for page in sorted(pages, key=lambda x: x['id']):
        print(f'  ID {page["id"]:2} : {page["name"]:<30} ({page["code"]})')

print(f'\nTOPLAM SAYFA: {total}')

print()
print(">> 4. PROJELER (YETKILENDIRME)")
print("-" * 80)
for i, proj in enumerate(PROJECTS, 1):
    print(f'{i}. {proj["name"]:<20} ({proj["code"]:12}) - {proj.get("country", "")}')

print()
print(">> 5. YAPILACAK ISLER")
print("-" * 80)
tasks = [
    '[DONE] Rol tabanli erisim kontrolu',
    '[DONE] Yetkilendirme matrisi',
    '[DONE] Kullanici ve rol yonetimi',
    '[TODO] FRACAS - Tarih filtresi',
    '[TODO] FRACAS - Icerik/Kategori filtresi',
    '[TODO] FRACAS - PDF/Excel indir',
    '[TODO] KPI - Tarih filtresi',
    '[TODO] KPI - Icerik/Kategori filtresi',
    '[TODO] KPI - PDF/Excel indir',
    '[INFO] Tum projeler icin veri dosyalari hazir mi - yukarida kontrol et',
]

for task in tasks:
    print(f'  {task}')

print()
print(">> 6. YENİ PROJE EKLEME ADIMLAR")
print("-" * 80)
print('''
1. app.py'de PROJECTS liste ekle:
   {'code': 'projeadi', 'name': 'Proje Adi', 'country': 'Ulke', 'flag': 'flag'}

2. data/projeadi/ klasorunu olustur

3. Gerekli dosyalari koy:
   - projeadi ANAHTARLAR LISTESI.XLSX
   - projeadi GUNLUK RAPOR.XLSX
   - Veriler.xlsx
   - Parca Verileri.xlsx
   - HBR LISTESI.XLSX
   - Bakim Onleyici.XLSX

4. /admin/yetkilendirme'de rol izinleri ayarla

5. Flask'i yeniden basla
''')

print("=" * 80)
print("ANALIZ TAMAMLANDI")
print("=" * 80)
