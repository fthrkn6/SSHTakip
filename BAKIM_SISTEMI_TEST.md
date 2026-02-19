# Bakım Sistemi Kurulum ve Test

## 📦 Gerekli Paketler

```bash
pip install Flask
pip install Flask-SQLAlchemy
pip install pandas
pip install openpyxl
```

Veya mevcut `requirements.txt` varsa:
```bash
pip install -r requirements.txt
```

## ▶️ Uygulamayı Başlatma

### Yöntemi 1: Python (Geliştirme)

```bash
cd c:\Users\fatiherkin\Desktop\bozankaya_ssh_takip
python app.py
```

Sonra browser'da git:
```
http://localhost:5000/bakim-planlari
```

### Yöntemi 2: VS Code Terminal

1. VS Code'da terminal aç (Ctrl+`)
2. 
```bash
python app.py
```

## 🧪 Quick Test

### Test 1: API Endpoint'lerini Test Et

```bash
# PowerShell'de Invoke-WebRequest veya curl kullınca

# Sheets listesi
curl -X GET http://localhost:5000/api/bakim-excel-sheets \
  -H "Authorization: Bearer <your_token>"

# Sheet items (6K örneği)
curl -X GET http://localhost:5000/api/bakim-sheet-items/6K \
  -H "Authorization: Bearer <your_token>"

# Transpoze tablo
curl -X GET http://localhost:5000/api/bakim-tablosu-transpose \
  -H "Authorization: Bearer <your_token>"
```

### Test 2: Browser'da Manual Test

1. `/bakim-planlari` sayfasını aç
2. **Tab 1 - Araç Durumu**:
   - Araçların listesini gör
   - Bir araç satırına tıkla → Modal açılmalı
   - "Tamamla" buttonu → Upload modal açılmalı

3. **Upload Modal Test**:
   - Dosya seç
   - İmza checkbox'ına tıkla
   - İmza canvas'ında imza çiz
   - "Yükle" buttonu
   - Başarı mesajı görülmeli
   - `logs/belgrad/Bakım/` klasöründe dosya kontrol et

4. **Tab 2 - Transpoze Tablo**:
   - Tüm araçların listesi görülmeli
   - Her hücre renkli olmalı
   - Herhangi bir hücreye tıkla → Detay modal açılmalı
   - Modal'da "Bakım Kartı Yükle" buttonu

## 🔧 Troubleshooting

### Flask port 5000 zaten kullanımda

```bash
# Windows'da port 5000'ı kullanan process'i bul
netstat -ano | findstr :5000

# Process'i sonlandir (PID'i kullan)
taskkill /PID <PID> /F
```

### ModuleNotFoundError: No module named 'xxx'

```bash
# Virtual environment aktif degil mi?
# Aktif et:

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Template'de JavaScript hataları

Browser console (F12) kontrol et:
- Network tab → `/api/bakim-tablosu-transpose` çalışıyor mu?
- Response'un valid JSON mi?

---

## 📊 Expected Database State

### Equipment tablosu

Şu kolonlar olmalı: `equipment_code`, `current_km`

```sql
SELECT equipment_code, current_km FROM Equipment 
WHERE project_code = 'belgrad' AND is_active = true;
```

## 📝 Belgrad-Bakım.xlsx Yapısı

Dosya yoluna: `data/belgrad/Belgrad-Bakım.xlsx`

**Sheet Adları:**
- 6K, 18K, 24K, 36K, 60K, 72K, 85K, 100K, 120K, 140K

**Her Sheet'te:**
- Satırlar: Bakım işleri (ör: "Motor yağı değişimi")
- Sütunlar: İş adı, açıklaması, ekipman, VS.

---

## 🎯 Başarılı Test Göstergeleri

✅ Upload modal açılıyor  
✅ İmza canvas'ında çizim yapılabiliyor  
✅ Dosya `logs/belgrad/Bakım/` klasörüne kaydediliyor  
✅ Transpoze tablo gösteriliyorvagas  
✅ Tablo hücreleri renklendirilmiş  
✅ Hücreye tıklandığında Belgrad-Bakım.xlsx sheet'i açılıyor  

---

**Test Tarihi:** 19.02.2026  
**Tester:** [Your Name]  
**Status:** ✅ PASS / ❌ FAIL
