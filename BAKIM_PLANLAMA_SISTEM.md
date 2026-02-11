# Bakım Planlama Sistemi - En Yakın Bakım Gösterimi

## Yapılan Değişiklikler

### 1. API Endpoint Değiştirildi (`app.py`)
**Rota**: `/api/bakim-verileri`

**Önceki Davranış**:
- API tüm 10 bakım seviyesini (6K, 18K, 24K, 36K, 60K, 70K, 100K, 140K, 210K, 300K) ayrı ayrı döndürüyordu
- Frontend'de "tablo boş olsun, uyarılar sadece mevcut KM sütununda" gerekiyordu

**Yeni Davranış**:
- API şimdi her araç için **en yakın bakımı** otomatik olarak hesaplar
- `nearest_maintenance` alanı eklendi: En yakın bakım bilgisi sadece bunu içeriyor
- `all_maintenances` alanı eklendi: Tüm bakım seviyeleri hala mevcut (modal detaylar için)

**JSON Yapısı**:
```json
{
  "tram_id": "1537",
  "tram_name": "Tramvay 1537",
  "current_km": 65000,
  "nearest_maintenance": {
    "level": "6K",
    "next_km": 66000,
    "km_left": 1000,
    "status": "warning",
    "works": [...]
  },
  "all_maintenances": {
    "6K": {...},
    "18K": {...},
    "24K": {...},
    ...
  }
}
```

### 2. Template Güncellendi (`templates/bakim_planlari.html`)

**Tablo Yapısı**:
- **Araç sütunu**: Araç adı ve ID
- **Mevcut KM sütunu**: Renklendirilmiş KM değeri (en yakın bakım statüsüne göre)
- **Sonraki Bakım sütunu**: Hangi bakım seviyesi en yakın
- **KM Farkı sütunu**: Kaç KM kaldığını gösterir
- **Durum sütunu**: Status badge (Normal ✓ / Uyarı ⚠ / Acil 🔴 / Geçmiş ✘)
- **İşlem sütunu**: "Detaylar" butonu

**Renk Kodlaması** (KM hücresi):
```
Yeşil (#d4edda)   - Normal (>2000 KM kaldı)
Sarı (#fff3cd)    - Uyarı (500-2000 KM kaldı)
Kırmızı (#f8d7da) - Acil (≤500 KM kaldı)
Gri (#e2e3e5)     - Geçmiş (tüm katlar geçmiş)
```

**Modal İşlevselliği**:
- Satıra tıklayın veya "Detaylar" butonuna basın
- Tüm bakım seviyeleri listelenir
- Her bakım için durumu ve işleri gösterir
- "Tamamla" butonu ile bakım durumunu işaretleyebilirsiniz
- Veriler localStorage'da saklanır

### 3. En Yakın Bakım Hesaplaması

**Algoritma**:
1. Her araç için tüm 10 bakım seviyesini hesapla
2. Her bakım seviyesinin **katlarını** bul (6K = 6, 12, 18, 24... km)
3. Bir sonraki bakım KM'sini belirle (current_km'den daha yüksek olan ilk kat)
4. km_left hesapla (next_km - current_km)
5. **En küçük pozitif km_left değerine sahip bakımı seç** = nearest
6. Eğer hiç pozitif km_left yoksa, son bakımı seç (300K)

**Örnek - Tramvay 1537 (65000 KM)**:
```
6K:   Next 66000 KM   | Left 1000 KM  | ⚠ WARNING  ← NEAREST (en küçük)
18K:  Next 72000 KM   | Left 7000 KM  | ✓ NORMAL
24K:  Next 72000 KM   | Left 7000 KM  | ✓ NORMAL
36K:  Next 72000 KM   | Left 7000 KM  | ✓ NORMAL
60K:  Next 120000 KM  | Left 55000 KM | ✓ NORMAL
70K:  Next 70000 KM   | Left 5000 KM  | ✓ NORMAL
...
```

### 4. Filtreleme Sistemi

Başard düğmeler:
- **Tümü**: Tüm araçları göster
- **Acil 🔴**: Sadece urgent araçları (≤500 KM)
- **Uyarı ⚠**: Sadece warning araçları (500-2000 KM)
- **Normal ✓**: Sadece normal araçları (>2000 KM)

Sayaçlar otomatik olarak güncellenir.

## Veri Kaynakları

1. **maintenance.json** - 10 bakım seviyesi ve işleri
2. **km_data.json** - Her araç için mevcut KM değeri
3. **Database** - Araç listesi (Equipment tablosu)

## Test Edildi

Tüm bileşenler test edilmiştir:
- ✓ API endpoint doğru yapıda verileri döndürüyor
- ✓ nearest_maintenance hesaplaması doğru
- ✓ Tüm status değerleri geçerli (normal/warning/urgent/overdue)
- ✓ Katlar (multiples) doğru hesaplanıyor
- ✓ Frontend JavaScript doğru şekilde verileri işliyor

## Kullanım

### Sayfaya Erişim
```
http://localhost:5000/bakim-planlari
```

### Araç Seçme
Tablodaki herhangi bir satıra tıklayın → Modal açılır

### Bakım Detaylarını Görme
Modal'da tüm bakım seviyeleri listelenmiştir:
- Her seviye için sonraki bakım KM'si
- Tamamlanacak işlerin listesi
- Status ve km_left değeri
- "Tamamla" / "✓ Tamamlandı" butonu

### Bakım Durumunu Kaydetme
- Modal'da bakımları "Tamamla" olarak işaretleyin
- "Değişiklikleri Kaydet" butonuna basın
- Veriler browser localStorage'da saklanır

## Notlar

- Tüm araçlar otomatik olarak 25 tram ID'si ile oluşturulur (km_data.json'dan)
- Her bakım seviyesinin işleri Belgrad-Bakım.xlsx dosyasından çıkartılmıştır
- KM değerleri test verilerdir (gerçek verilerle güncellenebilir)

---

**Sistem Hazır!** ✓
