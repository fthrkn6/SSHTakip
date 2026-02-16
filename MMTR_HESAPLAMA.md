# MTTR (Mean Time To Repair) Hesaplama Rehberi

## 📊 MTTR Nedir?

**MTTR (Mean Time To Repair)** - **Ortalama Tamir Süresi**, arızanın bildirimi ile tamir bitişi arasında geçen ortalama süreyi gösterir. Bakım ekibinin verimliliğinin temel göstergesidir.

### Formül

```
MTTR = Toplam Tamir Süresi (dakika) / Toplam Arıza Sayısı

MTTR (saat cinsinden) = Toplam Tamir Süresi (saat) / Toplam Arıza Sayısı
```

### Örnek Hesaplama

```
Örnek Senaryo:
- Toplam Tamir Süresi: 50,000 dakika
- Toplam Arıza Sayısı: 100
- MTTR = 50,000 / 100 = 500 dakika = 8 saat 20 dakika

Anlam: Her arıza ortalama 8 saat 20 dakikada tamir edilir
```

## 🔍 Dashboard'da Nasıl Hesalanıyor?

### 1. Veri Kaynakları

| Bileşen | Kaynak | Açıklama |
|---------|--------|---------|
| **Tamir Süresi** | Excel `Ariza Listesi` | "MTTR (dk)" sütunu |
| **Arıza Sayısı** | Excel `Ariza Listesi` | Toplam kayıt sayısı |
| **Başlangış Tarihi** | "Tamir Başlama Tarihi" | Arızanın tamir başlangıcı |
| **Bitiş Tarihi** | "Tamir Bitişi Tarihi" | Arızanın tamir bitişi |

### 2. Hesaplama Adımları

**Adım 1: Excel'den MTTR Sütununu Al**
```python
# logs/{project}/ariza_listesi/Ariza_Listesi_*.xlsx dosyasından

df = pd.read_excel(ariza_listesi_file, sheet_name='Ariza Listesi', header=3)
mttr_values = df['MTTR (dk)']  # Dakika cinsinden
```

**Adım 2: Boş Değerleri Filtrele ve Ortalamasını Hesapla**
```python
# NaN (Boş) değerleri ve sayısal olmayan değerleri dışarı bırak
mttr_values = pd.to_numeric(df['MTTR (dk)'], errors='coerce').dropna()

# Ortalama hesapla
mttr_average_minutes = mttr_values.mean()
```

**Adım 3: Dakikayı Saat:Dakika Formatına Çevir**
```python
hours = int(mttr_average_minutes // 60)
minutes = int(mttr_average_minutes % 60)

mttr_formatted = f"{hours}h {minutes}m"
# Örnek: "8h 20m"
```

### 3. Kod İmplementasyonu

**Dosya:** `routes/dashboard.py`

```python
def calculate_fleet_mttr():
    """
    Filo için MTTR (Mean Time To Repair) hesapla
    
    Returns:
        dict: {
            'mttr_minutes': float,      # Dakika cinsinden ortalama
            'mttr_formatted': str,      # "8h 20m" formatında
            'mttr_hours': float,        # Saat cinsinden ortalama
            'total_failures': int,      # Toplam arıza sayısı
            'unit': str                 # 'dakika (dk)'
        }
    """
```

## 📈 Yorumlama

### MTTR Değerleri Neler İfade Ediyor?

| MTTR Aralığı | Durum | Açıklama |
|--------------|-------|---------|
| **< 2 saat (120 dk)** | ✅ Çok İyi | Değişim merkezi çok verimli, hızlı tamir |
| **2-4 saat (120-240 dk)** | ✅ İyi | Standart tamir süresi, verimli |
| **4-8 saat (240-480 dk)** | ⚠️ Orta | Makul tamir süresi, parça beklentisi |
| **> 8 saat (480+ dk)** | ❌ Kötü | Uzun tamir süresi, sorun var |

### MTTR Arttığında Ne Olur?

- ❌ **Daha uzun tamir süreleri** → Araçlar daha uzun onarımda kalıyor
- ❌ **Operasyonel verimsizlik** → Filo kapasitesi düşüyor
- ❌ **Maliyetler artıyor** → Personel ve tedarikçi beklentisi
- ❌ **Müşteri memnuniyeti düşüyor** → Daha az kullanılabilir filo

### MTTR Azaldığında Ne Olur?

- ✅ **Daha kısa tamir süreleri** → Araçlar daha çabuk hizmetine döner
- ✅ **Operasyonel verimlilik artar** → Filo kapasitesi yükselir
- ✅ **Maliyetler azalır** → Daha az zaman = daha az maliyet
- ✅ **Müşteri memnuniyeti yükselir** → Daha çok kullanılabilir filo

## 🎯 İş Emri Tamamlama Yerine MTTR Neden?

### Eski Metrik: "Bugün Tamamlanan İş Emri"
```
❌ Günlük dalgalanmalara tabi
❌ Sadece sayısal değer, kalite göstermez
❌ Bakım verimliliği hakkında bilgi vermez
❌ Tamir süresini dikkate almıyor
```

### Yeni Metrik: MTTR
```
✅ Bakım ekibinin verimliliğinin göstergesi
✅ Tamir süresi = doğrudan maliyet gösterimi
✅ Trend analizi için daha uygun
✅ Endüstri standardı (ISO 13306, EN 15341, FMEA)
✅ Operasyonel etkinlik ölçüsü
```

## 🔧 Veri Güncellemesi

### MTTR Değeri Otomatik Güncellenir

- **Şu durumlarda MTTR recalculate edilir:**
  1. Dashboard yüklendikten sonra her sayfa görüntülemesinde
  2. Arıza Listesi Excel dosyası güncellendiğinde
  3. Tamir Bitişi Tarihi eklendiğinde

### Manual Güncelleme

```python
# Eğer veriler yanlışsa:

1. Excel dosyasını kontrol et:
   logs/{project}/ariza_listesi/Ariza_Listesi_*.xlsx
   
   - "MTTR (dk)" sütunu mevcut mu?
   - "Tamir Bitişi Tarihi" dolu mu?
   - Boş satırlar var mı?

2. Sayısal değerleri kontrol et:
   - MTTR değerleri sayısal olmalı (0, 100, 500 gibi)
   - "Text" biçiminde olursa otomatik dönüştürülür
```

## 📊 Dashboard Gösterimi

### Kart Bilgileri

```html
<!-- Dashboard'da görüntülenir -->
┌─────────────────────┐
│  MTTR               │
│  (Tamir Süresi)     │
│  ┌──────────────┐   │
│  │  8h 20m      │   │
│  ├──────────────┤   │
│  │ 100 arıza    │   │
│  └──────────────┘   │
└─────────────────────┘
```

### Bilgilendirici Yardım

Kart üzerine geldiğinde (hover) tooltip gösterilir:
- Dakika cinsinden ortalama: 500 dk
- Saat cinsinden: 8.33 saat
- Toplam arıza sayısı: 100

## 🔬 Teknik Detaylar

### Hesaplama Parametreleri

| Parametre | Değer | Açıklama |
|-----------|-------|---------|
| **Excel Sheet** | "Ariza Listesi" | MTTR (dk) sütunu |
| **MTTR Sütunu** | "MTTR (dk)" | Tamir süresi dakika cinsinden |
| **Header Row** | 3 | Excel başlık satırı |
| **Format** | Saat:Dakika | "8h 20m" |
| **Safeguard** | NaN kontrolü | Boş değerleri dışarı bırak |

### Hata Yönetimi

```python
# Eğer MTTR sütunu yoksa:
mttr_col = None  # Arama yapılır

# Eğer veri bulunamazsa:
except Exception as e:
    mttr_minutes = 0
    total_failures = 0
    mttr_formatted = '0m'
```

## 📝 Log ve Debug

### Debug Bilgileri

Console'da aşağıdaki log mesajları görüntülenebilir:

```
Excel MTTR okuma hatası: {error_details}
MTTR hesaplama hatası: {error_details}
```

### Verification

MTTR hesaplamasını doğrulamak için:

```python
# Python console'da:
from routes.dashboard import calculate_fleet_mttr
mttr_data = calculate_fleet_mttr()
print(mttr_data)

# Output:
# {
#     'mttr_minutes': 500.0,
#     'mttr_formatted': '8h 20m',
#     'mttr_hours': 8.33,
#     'total_failures': 100,
#     'unit': 'dakika (dk)'
# }
```

## 🚀 Best Practices

### MTTR'yi İyileştirmek İçin

1. **Bakım Merkezinin Verimliliğini Artırın**
   - Teknikerlerin eğitimini geliştirin
   - Uygun araç-gereç sağlayın
   - Çalışma organizasyonunu optimalleştirin

2. **Parça Temini Hızlandırın**
   - Stok yönetimini geliştiştirin
   - Tedarikçi sözleşmelerini iyileştirin
   - Acil durum parça deposu oluşturun

3. **Tanılama Sürelerini Kısaltın**
   - Teknik ekibi eğitin
   - Teşhis aletlerini güncelleyin
   - Sorun giderme protocolü oluşturun

4. **Veri Doğruluğunu Sağlayın**
   - Excel dosyalarını düzenli güncelleyin
   - Tamir bitişi saatini doğru kaydedin
   - MTTR (dk) sütunlarını otomatikleştirin

## 📚 Referanslar

- **ISO 13306:2018** - Maintenance terminology
- **EN 15341** - Maintenance – Key performance indicators
- **ISO 55000** - Asset Management
- **SAE JA1011** - Condition based Maintenance
- **FMEA** - Failure Mode and Effects Analysis

---

**Son Güncelleme:** Şubat 16, 2026  
**Sistem:** SSH Takip - Bozankaya Hafif Raylı Sistem  
**Versiyon:** 2.0 (MMTR'den MTTR'ye güncellendi)
