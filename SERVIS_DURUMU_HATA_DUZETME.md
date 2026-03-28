# Servis Durumu Sayfası - Hata Düzeltmesi (Fixed)

## Sorun (Problem)
Servis durumu sayfasında "Servis Dışı" seçildiğinde hata veriyordu.

## Kok Neden (Root Cause)
Turkish character encoding issues - typo with special Turkish letters ş vs ı

### Sorunlu Kod
```python
# routes/service_status.py - line 363 (BEFORE)
elif 'Dışı' in new_status or 'dişi' in new_status.lower() or 'ariza' in new_status.lower():
                                      ^^^^^ 
                                      WRONG - 'dişi' with 'i'
```

Sorun: Form tarafından gönderilen "Servis Dışı" değeri küçültüldüğünde "servis dışı" olur.
Bu durumda 'dişi' (regular 'i' with dot) aranırken 'dışı' (Turkish 'ı' without dot) var.

String matching başarısız olur ve status_code 'servis_disi' olarak atanmazsa backend hatalar veriyordu.

## Çözüm (Solution)

### Düzeltilen Lokasyonlar

1. **routes/service_status.py - line 363**
   ```python
   # BEFORE
   elif 'Dışı' in new_status or 'dişi' in new_status.lower() or 'ariza' in new_status.lower():
   
   # AFTER  
   elif 'Dışı' in new_status or 'dışı' in new_status.lower() or 'ariza' in new_status.lower():
   ```

2. **routes/service_status.py - line 273** (aynı issue)
   ```python
   # BEFORE
   elif 'Dışı' in service_status or 'dişi' in service_status.lower() or 'ariza' in service_status.lower():
   
   # AFTER
   elif 'Dışı' in service_status or 'dışı' in service_status.lower() or 'ariza' in service_status.lower():
   ```

3. **routes/service_status.py - line 17** (Missing import)
   ```python
   # BEFORE
   from utils_availability import (
       log_service_status_change
   )
   
   # AFTER
   from utils_availability import (
       log_service_status_change,
       AvailabilityCalculator
   )
   ```

4. **routes/dashboard.py - line 561**
   ```python
   # BEFORE
   elif 'Dışı' in service_status or 'disi' in service_status.lower() or 'ariza' in service_status.lower():
                                    ^^^^^ WRONG (missing dot)
   
   # AFTER
   elif 'Dışı' in service_status or 'dışı' in service_status.lower() or 'ariza' in service_status.lower():
   ```

## Doğrulama (Verification)

✅ `AvailabilityCalculator` import eklendi
✅ Turkish character matching düzeltildi
✅ All service status logging functions tested and working
✅ Endpoint responding correctly (returns 401 unauthorized without login, 200 OK with JSON response when authenticated)

## Test Sonuçları

Yapılan testler:
1. ✅ All imports successful
2. ✅ Equipment lookup working
3. ✅ log_service_status_change() working
4. ✅ AvailabilityCalculator.calculate_daily_availability() working
5. ✅ ExcelGridManager working
6. ✅ Endpoint /servis/durumu/log responding (200 OK when authenticated)

## İlişkili Dosyalar
- routes/service_status.py - Servis durumu endpoint
- routes/dashboard.py - Dashboard status display
- utils_availability.py - Availability calculation utilities
