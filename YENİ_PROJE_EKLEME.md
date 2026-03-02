# YENİ PROJE EKLEME KILAVUZU

## Hızlı Yol (Otomatik Setup)

```bash
# Script'i çalıştır
python setup_new_project.py

# Veya kodda direkt çağır:
from setup_new_project import create_new_project

create_new_project(
    project_name='ankara',
    vehicle_codes=[5001, 5002, 5003, 5004, 5005]
)
```

## Adım Adım Yol (Manuel)

### 1. Klasör Oluştur
```
data/
└── ankara/          ← Yeni klasör (proje adı)
    ├── Veriler.xlsx
    ├── maintenance.json
    └── ...
```

### 2. Veriler.xlsx Hazırla

**Gerekli:** Sheet name = **"Sayfa2"**

| Araç Kodu | Araç Adı | Sistem | KM Hedefi |
|-----------|----------|--------|-----------|
| 5001 | Ankara-1 | TR-A01 | 200000 |
| 5002 | Ankara-2 | TR-A02 | 200000 |
| 5003 | Ankara-3 | TR-A03 | 200000 |

**Column A: Araç Kodları** (sayısal veya string)

### 3. maintenance.json Oluştur

```json
{
  "15K": {
    "km": 15000,
    "works": ["BOZ-001"]
  },
  "30K": {
    "km": 30000,
    "works": ["BOZ-002"]
  },
  "60K": {
    "km": 60000,
    "works": ["BOZ-003", "BOZ-004"]
  },
  "90K": {
    "km": 90000,
    "works": ["BOZ-005"]
  },
  "120K": {
    "km": 120000,
    "works": ["BOZ-006", "BOZ-007"]
  },
  "200K": {
    "km": 200000,
    "works": ["BOZ-008"]
  }
}
```

### 4. Sistem Ready!

Sistem otomatik olarak:
- ✅ Excel'yi okur
- ✅ Database'ye yazır
- ✅ Bakım planlarını hazırlar
- ✅ Admin panelde gösterir

## Veri Kaynakları (Excel Sütunları)

### Sayfa2 - Araç Listesi
| Sütun | Adı | Zorunlu | Örnek |
|-------|-----|---------|-------|
| A | Araç Kodu | ✓ | 5001 |
| B | Araç Adı | | Ankara-1 |
| C | Sistem | | TR-A01 |
| D | KM | | 45000 |
| E | Hedef KM | | 200000 |

### Diğer Sheet'ler (Opsiyonel)
- **fracas**: Arıza kayıtları
- **km_log**: KM geçmişi
- **parts**: Yedek parça

## Otomatik Senkronizasyon

Excel her değiştirildiğinde Database otomatik güncellenir:

```
Excel değişikliği
    ↓
API çağrısı
    ↓
sync_equipment_with_excel() çalışır
    ↓
Database güncellenir
    ↓
UI yenilenir ✅
```

## Örnek: İzmir Projesi Ekle

```python
from setup_new_project import create_new_project

# İzmir projesi oluştur
create_new_project(
    project_name='izmir',
    vehicle_codes=[7001, 7002, 7003, 7004, 7005, 7006, 7007]
)
```

## Sorun Giderme

### Excel dosyası bulunamadı
- `data/{proje_adi}/Veriler.xlsx` dosyasının varlığını kontrol et
- Dosya adının tam olarak "Veriler.xlsx" olduğundan emin ol

### Araçlar gösterilmiyor
- Excel'de Sayfa2 sayfasının varlığını kontrol et
- Column A'da araç kodları olup olmadığını kontrol et

### Bakım planları boş
- `maintenance.json` dosyasını kontrol et
- JSON formatı doğru mu kontrol et

## Proje Silme

```bash
cd data/
rm -r ankara/  # Linux/Mac
rmdir /s ankara  # Windows PowerShell
```

## Admin Panelinde Proje Seçme

1. Login et
2. Sağ üst köşede "Proje Seç" dropdown'ı
3. Yeni proje görülecek otomatik
4. Tıkla → Sistem yeni projeyi yükler

---

**ÖNEMLİ:** Sistem **tek kaynak doğruluğu** prensibi kullanır:
- ✓ Excel ana kaynak (Sayfa2)
- ✓ Database Excel'den türetilir
- ✓ Her API çağrısında otomatik senkronizasyon
