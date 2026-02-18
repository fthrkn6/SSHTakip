# Form Alanları → Excel Hücreleri Mapping Tablosu

## ❌ PROBLEM: Form Alanları ile HBR Kodu Uyumsuz!

### Form'da Olup, HBR Code'da Kullanılacak Alanlar

| Form Alan Adı | Form name="" | HBR Code'da Kullanılıyor? | Excel Hücresi | Kullanılacak Form Alanı |
|---|---|---|---|---|
| **Araç Numarası** | arac_numarasi | ❌ HAYIR | A6 | ✓ TO BE USED |
| **Araç Modülü** | arac_module | ❌ HAYIR (kullanılırken arac_modulu olarak aranıyor) | D19 | arac_module → arac_modulu |
| **Araç KM** | arac_km | ✓ form_data.get('km') AMA form'da arac_km | G7 | arac_km → km |
| **Hata Tarihi** | hata_tarih | ✓ form_data.get('ariza_tarihi') AMA form'da hata_tarih | G6 | hata_tarih → ariza_tarihi |
| **Sistem** | sistem | ❌ HAYIR | - | - |
| **Tedarikçi** | tedarikci | ✓ | J7 | ✓ |
| **Arıza Sınıfı** | ariza_sinifi | ✓ | G9/G10/G11 | ✓ |
| **Arıza Tipi** | ariza_tipi | ✓ | H9/A12/E12 | ✓ |
| **Arıza Tanımı** | ariza_tanimi | ✓ | B17 | ✓ |
| **Parça Seri No** | parca_seri_no | ✓ | G19 | ✓ |
| **HBR Fotoğrafı** | hbr_fotograf | ✓ | B20 | ✓ |

---

## ✅ DÜZELTILMESI GEREKEN MAPPING

### HBR Excel'de Doldurulacak Hücreler

| Excel Hücresi | Alan Adı | Form'da Aranıyor | Form'da Gönderiliyor | SORUN |
|---|---|---|---|---|
| **A6** | Malzeme No / Araç Numarası | `malzeme_no` | `arac_numarasi` | ✓ FIX: form_data.get('arac_numarasi') |
| **D6** | Malzeme Adı / Araç Modülü | `malzeme_adi` | `arac_module` | ✓ FIX: form_data.get('arac_module') |
| **E6** | Rapor Tarihi | Sistematik | Otomatik (datetime.now()) | ✓ OK |
| **G6** | Arıza Tarihi | `form_data.get('ariza_tarihi')` | `hata_tarih` | ✓ FIX: form_data.get('hata_tarih') |
| **I6** | NCR Numarası | Sistematik | Otomatik (BOZ-NCR-XXX) | ✓ OK |
| **G7** | KM | `form_data.get('km')` | `arac_km` | ✓ FIX: form_data.get('arac_km') |
| **J7** | Tedarikçi | `form_data.get('tedarikci')` | `tedarikci` | ✓ OK |
| **E8** | Müşteri Kodu | Sistematik | veriler.xlsx'ten | ✓ OK |
| **F8** | Tespit Yöntemi (Bozankaya) | Sistematik | current_user.username | ✓ OK |
| **H8** | Müşteri Bildirimi | `form_data.get('muslteri_bildirimi')` | ❌ HAYIR (form'da yok) | ⚠️ MISSING FIELD |
| **G9/G10/G11** | Arıza Sınıfı | `form_data.get('ariza_sinifi')` | `ariza_sinifi` | ✓ OK |
| **H9/A12/E12** | Arıza Tipi | `form_data.get('ariza_tipi')` | `ariza_tipi` | ✓ OK |
| **B17** | Arıza Tanımı | `form_data.get('ariza_tanimi')` | `ariza_tanimi` | ✓ OK |
| **D19** | Araç Modülü | `form_data.get('arac_modulu')` | `arac_module` | ✓ FIX: form_data.get('arac_module') |
| **G19** | Parça Seri No | `form_data.get('parca_seri_no')` | `parca_seri_no` | ✓ OK |
| **B20** | Fotoğraf | request.files['hbr_fotograf'] | `hbr_fotograf` | ✓ OK |
| **B22** | SSH Sorumlusu | Sistematik | current_user.username | ✓ OK |

---

## 📝 ÖZET: Yapılması Gereken Değişiklikler

### HBR Code'da (app.py) Yapılması Gereken Düzeltmeler:
1. ❌ `malzeme_no` → ✓ `arac_numarasi`
2. ❌ `malzeme_adi` → ✓ `arac_module` (ama liste için join etmesi lazım)
3. ❌ `ariza_tarihi` → ✓ `hata_tarih`
4. ❌ `km` → ✓ `arac_km`
5. ❌ `arac_modulu` → ✓ `arac_module` (zaten kullanılıyor, ok)
6. ❌ `muslteri_bildirimi` → ⚠️ Form'da bu alan yok (kaldırılabilir yada form'a eklenmeli)

### Örnek Düzeltme:
```python
# ESKI (❌ YANLIŞ):
malzeme_no = form_data.get('malzeme_no', '')      # Form'da yok!
malzeme_adi = form_data.get('malzeme_adi', '')     # Form'da yok!
km = form_data.get('km', '')                        # Form'da arac_km var!
ariza_tanimi = form_data.get('ariza_tanimi', '')   # ✓ OK
ariza_tipi = form_data.get('ariza_tipi', '')       # ✓ OK

# YENİ (✓ DOĞRU):
arac_numarasi = form_data.get('arac_numarasi', '')           # ✓
arac_modules = request.form.getlist('arac_module')            # ✓
arac_modulu_str = ', '.join(arac_modules) if arac_modules else ''  # ✓
arac_km = form_data.get('arac_km', '')                        # ✓  
hata_tarih = form_data.get('hata_tarih', '')                 # ✓
ariza_tanimi = form_data.get('ariza_tanimi', '')             # ✓
ariza_tipi = form_data.get('ariza_tipi', '')                 # ✓
parca_seri_no = form_data.get('parca_seri_no', '')           # ✓
tedarikci = form_data.get('tedarikci', '')                   # ✓
```

---

## ⚠️ EKSIK FORM ALANI

Form'da olması lazım ama olmayan:
- **`muslteri_bildirimi`** - Currently code expects this but form doesn't have it
  - Çözüm: Form'a ekle ya da code'dan kaldır

---

## ✅ SONUÇ

HBR Excel dosyası doldurulmadığı için, app.py HBR code'unu formun gerçek alan adlarına göre güncellemek lazım.
