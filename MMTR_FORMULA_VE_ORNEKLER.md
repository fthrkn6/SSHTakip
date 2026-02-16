# MMTR Formülü ve Hesaplama Örneği

## 📐 MMTR Temel Formülü

```
MMTR = Toplam Operasyon Saati (veya Mesafesi)
       ────────────────────────────────────────
            Toplam Arıza Sayısı
```

### Birim Açıklaması

| Birim | Açıklama | Örnek |
|------|---------|--------|
| **km/arıza** | Her 1 arızaya kaç KM işletme | 5,000 km ÷ 1 arıza |
| **saat/arıza** | Her 1 arızaya kaç saat işletme | 100 saat ÷ 1 arıza |
| **aylar arası** | Her arıza kaç ay arayla meydana gelir | 2 ay ÷ 1 arıza |

**SSH Takip'te kullanılan:** `km/arıza` (en yaygın ve uygulanabilir)

---

## 🧮 Gerçek Hesaplama Örneği

### Senaryo: Belgrad Filosu (25 Tramvay)

**Veri Giriş:**
```
Tramvay Listesi (1531-1555):
┌──────┬──────────┐
│Tram# │ Güncel KM│
├──────┼──────────┤
│1531  │ 150,000  │
│1532  │ 148,000  │
│1533  │ 152,000  │
│1534  │ 149,500  │
│1535  │ 151,000  │
│...   │  ...     │
│1555  │ 145,000  │
└──────┴──────────┘

Toplam: 3,750,000 KM
```

**Arıza Verisi (Excel'den):**
```
Ariza Listesi'nden:
┌─────────┬──────────────┐
│ FRACAS  │ Araç No      │
├─────────┼──────────────┤
│ A-2401  │ TRN-1531     │
│ A-2402  │ TRN-1532     │
│ A-2403  │ TRN-1533     │
│ ...     │ ...          │
│ A-2600  │ TRN-1555     │
└─────────┴──────────────┘

Toplam Arıza: 750 adet
```

### Hesaplama Adımları

**Adım 1: Toplam Filo KM**
```
⊕ Tramvay 1531:  150,000 km
⊕ Tramvay 1532:  148,000 km
⊕ Tramvay 1533:  152,000 km
⊕ Tramvay 1534:  149,500 km
⊕ Tramvay 1535:  151,000 km
...
⊕ Tramvay 1555:  145,000 km
━━━━━━━━━━━━━━━━━━━━━━━━
= 3,750,000 km
```

**Adım 2: Toplam Arıza Sayısı**
```
Excel'de "Ariza Listesi" sheet'inde
boş satırlar hariç toplam satır sayısı
= 750 arıza
```

**Adım 3: MMTR Hesapla**
```
MMTR = 3,750,000 km ÷ 750 arıza
     = 5,000 km/arıza
     
Anlam: Her 5,000 km işletmede bir arıza meydana gelir
```

---

## 📊 Grafik Gösterim

### MMTR Trendleri

```
MMTR Değeri (km/arıza) vs Zaman

     │
8000 │        ↗ İyi Yönetim
     │       ╱  (MMTR Arttı)
6000 │      ╱
     │     ╱
4000 │    ╱─────── Uygun Seviye (5000)
     │   ╱
2000 │  ╱ ↘ Kötü Performans
     │     ╲ (MMTR Düştü)
   0 │──────────────────────
     │ Şub  Mar  Nis  May  Haz
     
     ← Daha Kötü | Daha İyi →
```

### Arıza Sıklığı

```
Eğer MMTR = 5,000 km/arıza ise:

Tramvay her 5,000 km'de bir arızalanır:

Km:     0 ─────┬────── 5000 ─────┬────── 10000 ────┬──── 15000
         │     │  │      │  │    │  │     │   │    │
Arıza:   │     └──┘      │  └────┘  │     │   └────┘
         │                │                │
         ×                 ×                 ×
      (0 km)          (5000 km)          (10000 km)
```

---

## 🎯 MMTR Değer Aralıkları

### Filo Güvenilirlik Sınıflandırması

```
┌─────────────────┬─────────┬─────────────────────────────┐
│ MMTR Aralığı    │ Durum   │ Yorum                       │
├─────────────────┼─────────┼─────────────────────────────┤
│ > 15,000 km     │ ★★★★★  │ MÜKEMMEL                    │
│                 │ EXCELl  │ ✓ Yeni veya çok iyi bakımlı│
│                 │         │ ✓ Minimal bakım maliyeti   │
├─────────────────┼─────────┼─────────────────────────────┤
│ 10,000 - 15,000 │ ★★★★   │ ÇOK İYİ                     │
│                 │ GOOD    │ ✓ Güvenilir filo           │
│                 │         │ ✓ Etkili bakım programı    │
├─────────────────┼─────────┼─────────────────────────────┤
│ 5,000 - 10,000  │ ★★★    │ ORTA (Hedef)                │
│                 │ FAIR    │ ✓ Makul güvenilirlik       │
│                 │         │ ✓ Standart bakım gerekli   │
├─────────────────┼─────────┼─────────────────────────────┤
│ 2,000 - 5,000   │ ★★     │ ZAYIF                       │
│                 │ POOR    │ ✗ Sık arızalar             │
│                 │         │ ✗ Yüksek bakım maliyeti    │
├─────────────────┼─────────┼─────────────────────────────┤
│ < 2,000 km      │ ★       │ ÇOK ZAYIF                   │
│                 │ CRITICAL│ ✗ Çok sık arızalar         │
│                 │         │ ✗ Acil kararlar gerekli    │
└─────────────────┴─────────┴─────────────────────────────┘
```

---

## 📈 Örnek Senaryo Analizleri

### Senaryo 1: Yeni Filo

```
Tramvay Yaşı: 0-5 yıl
Bakım Kalitesi: Çok İyi

Veri:
- Toplam KM: 500,000 km
- Toplam Arıza: 20 adet

MMTR = 500,000 ÷ 20 = 25,000 km/arıza

Değerlendirme: ★★★★★ MÜKEMMEL
→ Beklendiği gibi - yeni araç
→ Bakım stratejisi başarılı
→ İçerisinde kalmak için trend sürdür
```

### Senaryo 2: Orta Yaşlı Filo

```
Tramvay Yaşı: 10-15 yıl
Bakım Kalitesi: Normal

Veri:
- Toplam KM: 3,750,000 km
- Toplam Arıza: 750 adet

MMTR = 3,750,000 ÷ 750 = 5,000 km/arıza

Değerlendirme: ★★★ ORTA (Hedef)
→ Yaş göz önüne alındığında normal
→ Bakım planlama etkili
→ Preventif bakımı arttırmayı düşün
```

### Senaryo 3: Yaşlı / Sorunlu Filo

```
Tramvay Yaşı: 20+ yıl
Bakım Kalitesi: Yetersiz

Veri:
- Toplam KM: 2,000,000 km
- Toplam Arıza: 1500 adet

MMTR = 2,000,000 ÷ 1500 = 1,333 km/arıza

Değerlendirme: ★ ÇOK ZAYIF
→ Sık arızalar - ciddi sorun
→ Bakım stratejisi gözden geçirilmeli
→ Parça yenilemesi veya araç değişimi gerekebilir
→ Operasyonel uygulanabilirlik sorgulanacak
```

---

## 🔍 MMTR Hesaplamasında Dikkat Edilecek Noktalar

### Doğru Hesaplama Kriterleri

```
✅ DO's (Doğru Yapılanlar)
├── Excel dosyasından TÜÜN arızaları say
├── Boş satırları hariç tut
├── Sadece "Ariza Listesi" sheet'ini kullan
├── Header row = 3 (Excel'de doğrulandı)
├── Tüm tram KM'lerini topla (1531-1555)
├── Güncellenmiş KM değerlerini kullan
└── Division by zero koruması ekle

❌ DON'Ts (Yanlış Yapılanlar)
├── Filtreleme ile arıza sayısını azaltma
├── Sadece açık arızaları say
├── Belirli tarih aralığı seç (tüm geçmiş kullan)
├── KM yerine saat seç (tutarsız)
├── Sadece 1 tram için hesapla (filo ortalaması gerek)
├── Eski KM değerleri kullan
└── Division by zero'yu görmezden gel
```

---

## 🛠️ Kodda MMTR Hesaplaması

### Gerçek Kod (dashboard.py)

```python
def calculate_fleet_mmtr():
    """MMTR hesapla: Toplam KM / Toplam Arıza"""
    
    # 1. Toplam arıza sayısı
    df_failures = pd.read_excel(
        ariza_listesi_file, 
        sheet_name='Ariza Listesi', 
        header=3
    )
    total_failures = len(df_failures[df_failures.iloc[:, 0].notna()])
    
    # 2. Toplam filo KM
    tram_equipments = Equipment.query.filter(
        Equipment.equipment_code >= '1531',
        Equipment.equipment_code <= '1555',
        Equipment.parent_id == None,
        Equipment.project_code == current_project
    ).all()
    
    total_fleet_km = sum(
        getattr(tram, 'current_km', None) or 0 
        for tram in tram_equipments
    )
    
    # 3. MMTR hesapla
    if total_failures == 0:
        total_failures = 1  # Division by zero
    
    mmtr = round(total_fleet_km / total_failures, 1)
    
    return {
        'mmtr': mmtr,                              # 5000.0
        'total_failures': total_failures,          # 750
        'total_fleet_km': total_fleet_km,          # 3750000
        'fleet_size': len(tram_equipments),        # 25
        'unit': 'km per failure'
    }
```

### Template'de Kullanım (dashboard.html)

```html
<!-- MMTR Kartı -->
<div class="metric-card">
    <h6>MMTR<br><small>(km/arıza)</small></h6>
    
    <!-- Ana değer -->
    <div class="metric-value text-info">
        {{ stats.mmtr.mmtr|int }}
    </div>
    
    <!-- Alt bilgi -->
    <small class="text-muted d-block mt-2">
        {{ stats.mmtr.total_failures }} arıza
    </small>
</div>
```

**Render Çıktısı:**
```
┌──────────────────┐
│  MMTR            │
│  (km/arıza)      │
│                  │
│  5,000 km        │
│                  │
│  750 arıza       │
└──────────────────┘
```

---

## 📊 MMTR vs Diğer Metrikler

### Karşılaştırma Tablosu

| Metrik | Tanım | Aralığı | Kullanım |
|--------|-------|---------|----------|
| **MMTR** | Arızalar arası ortalama mesafe | 1,000 - 50,000 km | Filo güvenilirliği |
| **MTTR** | Ortalama onarım süresi | 1 - 24 saat | Onarım verimliliği |
| **Availability** | Filo kullanılabilirlik oranı | 0 - 100% | Operasyon kapasitesi |
| **Downtime %** | Arızalı olma yüzdesi | 0 - 100% | Verimsizlik oranı |
| **Cost/KM** | km başına bakım maliyeti | 10 - 100 TL | Ekonomik verimlilik |

---

## 🎓 Akademik Kaynaklar

### MMTR Standardında Kullanım

- **ISO 13306:2018** - Tanımı: "Mean Time to Repair veya Mean Time Between Removals"
- **EN 15341** - KPI'lar: MMTR, MTTR, Availability kombinasyonu
- **SAE JA1011** - Condition Based Maintenance için temel metrik

### Türkçe Denk Terimler

| İngilizce | Türkçe | Alternatif |
|-----------|     |---|
| MMTR | Arızalar Arası Ortalama Zaman | Ortalama Arıza Aralığı |
| MTBF | Mean Time Between Failures | - |
| MTTR | Ortalama Onarım Süresi | - |

---

## 🚀 MMTR'yi İyileştirme Stratejileri

### Kısa Vadeli (1-3 ay)

```
1. Planlı Bakım Artırma (PM)
   └─ Yağlama, soğutma sıvısı kontrolü
   
2. Parça Kalitesi Kontrol
   └─ Orijinal özeltikler vs Benzer ürünler
   
3. Operasyonel Uygulamalar
   └─ Sürücü eğitimi, hızlı başlangıç
```

### Orta Vadeli (3-12 ay)

```
1. Sistem İyilemeleri
   └─ Sorunlu bileşenleri redesign
   
2. Tedarikçi Değeri
   └─ Yeni parça tedarikçileri test et
   
3. Verileri Analiz
   └─ Sık arızalanan bileşenleri belirle
```

### Uzun Vadeli (12+ ay)

```
1. Filo Yenileme
   └─ Yaşlı araçları değiştir
   
2. Teknoloji Yükseltmesi
   └─ Elektrikli araçlara geç
   
3. Bakım Merkezi Kuruluşu
   └─ İn-house kapasitesi artır
```

---

**Bilimsel Temel:** ISO 13306:2018  
**Pratik Uygulama:** SSH Takip - Bozankaya  
**Son Güncelleme:** Şubat 16, 2026
