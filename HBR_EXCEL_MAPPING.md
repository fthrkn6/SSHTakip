# HBR Excel Dosyası - Hücre Haritalaması

## Form Verileri → Excel Hücre Yazışması

| Excel Hücresi | Veri Adı | Form Alanı | Açıklama | Durum |
|---|---|---|---|---|
| A6 | parca_kodu | equipment_code | Bileşen/Parça Numarası | ✅ |
| D6 | parca_adi | Parça Adı | Nesne Kısa Metni | ✅ |
| E6 | Rapor Tarihi | - | Sistemi Tarihi (today) | ✅ |
| G6 | hata_tarih | ariza_tarihi | Arıza Tarihi | ✅ |
| I6 | ncr_number | - | NCR Numarası (BEL25-NCR-001) | ✅ |
| A8 | arac_numarasi | arac_numarasi | Araç Numarası | ⚠️ append |
| G7 | arac_km | arac_km | Araç Kilometre | ✅ |
| I7 | tedarikci | tedarikci | Tedarikçi Adı | ✅ |
| E8 | musteri_code | - | Müşteri Kodu (Veriler.xlsx C3) | ⚠️ append |
| F8 VEYA H8 | [X] | ariza_tespit_yontemi | Tespit Yöntemi | ⚠️ koşullu |
| G9 | [X] | ariza_sinifi | Kritik | ⚠️ koşullu A |
| G10 | [X] | ariza_sinifi | Yüksek/Fonksiyonel | ⚠️ koşullu B |
| G11 | [X] | ariza_sinifi | Orta/Düşük | ⚠️ koşullu C/D |
| H9 | [X] | ariza_tipi | İlk Defa | ⚠️ koşullu |
| A12 | [X] | ariza_tipi | Tekrarlayan (Aynı Araç) | ⚠️ koşullu |
| E12 | [X] | ariza_tipi | Tekrarlayan (Farklı Araç) | ⚠️ koşullu |
| B17 | ariza_tanimi | tanimlama | Arıza Tanımı | ✅ |
| D19 | arac_modulu | arac_modulu | Araç Modülü | ✅ |
| G19 | parca_seri_no | parca_seri_no | Parça Seri Numarası | ✅ |
| B20 | Resim | hbr_fotograf | Fotoğraf (300x300px) | ✅ PIL |
| B24 | Hata Bildiren | - | Kullanıcı Adı Soyadı | ✅ |
| C24 | Hata Bildiren Kullanıcı | - | Kullanıcı Adı Soyadı | ✅ |
| D24 | Hata Bildiren Kullanıcı (2) | - | Kullanıcı Adı Soyadı | ✅ |

---

## ⚠️ POTENSİYEL HATALAR

### 1. **Tespit Yöntemi (F8/H8) - HATA RİSKİ YÜKSEKTİ**
```python
if 'bozankaya' in current_user.username.lower() or 'Bozankaya' in ariza_tespit_yontemi:
    write_cell(ws, 'F8', '[X]', append=True)  # Bozankaya
elif 'müşteri' in ariza_tespit_yontemi.lower():
    write_cell(ws, 'H8', '[X]', append=True)  # Müşteri
```
**PROBLEM:** 
- Eğer ikisi de match etmez ise hiç hücre seçilmez ❌
- `current_user.username.lower()` vs `ariza_tespit_yontemi` tutarsızlı
- Form'dan 'Bozankaya' yazı gelirse çalışır ama farklı text varsa hata

**FİX ÖNERİSİ:** Kesin değerler kullan (select dropdown)

---

### 2. **Arıza Sınıfı (G9/G10/G11) - MANTIK HATASI**
```python
sinif_mapping = {}
if 'A' in ariza_sinifi or 'Kritik' in ariza_sinifi:
    sinif_mapping = {'cell': 'G9', 'type': 'Kritik'}
elif 'B' in ariza_sinifi or 'Yüksek' in ariza_sinifi:
    sinif_mapping = {'cell': 'G10', 'type': 'Yüksek'}  # ← G10
elif 'C' in ariza_sinifi or 'Orta' in ariza_sinifi:
    sinif_mapping = {'cell': 'G11', 'type': 'Orta'}    # ← G11
elif 'D' in ariza_sinifi or 'Düşük' in ariza_sinifi:
    sinif_mapping = {'cell': 'G11', 'type': 'Düşük'}   # ← G11 (PROBLEM!)
```
**PROBLEM:** 
- Düşük sınıfı da G11'e yazılıyor, Orta ile aynı hücre ❌
- Excel'de "Orta" ve "Düşük" için ayrı checkbox var mı?

---

### 3. **Arıza Tipi (H9/A12/E12) - MULTIPLE SEÇIM HATASI**
```python
if 'ilk' in ariza_tipi_lower:
    write_cell(ws, 'H9', '[X]')  # İlk defa

if ('tekrarlayan' in ariza_tipi_lower) and ('aynı' in ariza_tipi_lower):
    write_cell(ws, 'A12', '[X]')  # Aynı araçta

if ('tekrarlayan' in ariza_tipi_lower) and ('farklı' in ariza_tipi_lower):
    write_cell(ws, 'E12', '[X]')  # Farklı araçta
```
**PROBLEM:**
- `if/if/if` kullanıldığı için **AYNI ANDA birden çok [X] yazılabilir** ❌
- Form'da "tekrarlayan_ayni_arac" seçilince → "tekrarlayan" kelimesi hem A12 hem E12'ye yazabilir
- Formatta belki strings arasında farklılık var ('teknarlayan' vs 'tekrarlayan_ayni_arac')

**FİX ÖNERİSİ:** `if/elif/elif` yap veya form'dan kesin enum gönder

---

### 4. **append=True Parametresi - UYARSI**
```python
write_cell(ws, 'A8', arac_numarasi, append=True)
write_cell(ws, 'E8', musteri_code, append=True)
write_cell(ws, 'F8', '[X]', append=True)
```
**PROBLEM:**
- `append=True` kullanılan hücreler merged olup olmadığı kontrol edilmiyor
- Eğer A8, E8, F8 vb merged hücrelerse unmerge → yaz → remerge yapılmaya çalışılır
- Bu işlem başarısız olursa veri yazılmayabilir

---

### 5. **Müşteri Kodu (E8) - VERİ KAYNAĞI HATASı**
```python
veriler_path = os.path.join('data', project, 'veriler.xlsx')
musteri_code = veriler_ws['C3'].value or 'equipment_code'
```
**PROBLEM:**
- veriler.xlsx dosyası olmayabilir → fallback olur ❌
- C3 hücresi boş olabilir → 'equipment_code' string'i yazılır ❌
- Gerçek müşteri kodu yazılmayabilir

**FİX ÖNERİSİ:** Form'dan müşteri seç ve eksplisit yolla

---

### 6. **B22 vs B24 SAKARTI** 
```python
# write_cell(ws, 'B22', current_user.username)  # YOKSAY
write_cell(ws, 'B24', kullanici_adi_soyadi)  # KULLAN
```
**PROBLEM:**
- B22 commented out ❌ (SSH Sorumlusu boş kalıyor)
- Eğer Excel'de B22'de "SSH Sorumlusu" label varsa template sorun

---

## ✅ YENİ VE GEREKLI ALANLAR

Form'da bu alanlar var ama Excel'e yazılmıyor:
- `detay` - Arıza Detayı/Açıklaması
- `sinyaladi` - Signal Adı
- `sinyaltipi` - Signal Tipi
- `sistem` - Sistem Adı
- `tanimlama` - Tanımlama (B17'ye yazılıyor ✅)

**ÖNERİ:** Detay ve Sistem adı da Excel'e yazılmalı (varsa)

---

## 🔧 TAVSIYE EDILEN FİX'LER

1. **Arıza Sınıfı:** Düşük için ayrı hücre (G12 mi?) kontrol et
2. **Arıza Tipi:** `if/elif/elif` yap, multiple [X] yazılmasını engelle
3. **Tespit Yöntemi:** Form'da dropdown select kullan, hard "bozankaya" string karşılaştırması yapma
4. **Müşteri:** Form'dan ekrana müşteri seç, E8'e yaz
5. **B22:** SSH Sorumlusu alanını aktif et
6. **Detay:** B19 veya başka hücreye `detay` de yazıldığını kontrol et

---

## FORM → EXCEL FLOW ÖZETİ

```
Arıza Bildir Formu
    ↓
app.py → quikAdd() (POST /dashboard/quikAdd)
    ↓
HBR Excel Template Oku
    ↓
Hücreler Yaz (⚠️ conditional logic zararlı olabilir)
    ↓
Resim Ekle (PIL - B20)
    ↓
BEL25-NCR-XXX.xlsx Kaydet
    ↓
logs/BELGRAD/HBR/ klasöre
```
