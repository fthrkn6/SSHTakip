# app.py Code Refactoring Guide

## Overview
This guide shows the specific sections in app.py that should be refactored for better maintainability.

---

## Issue 1: Duplicate Imports in Functions

### Current State - Lines 217-226 in dashboard():
```python
from datetime import datetime
import pandas as pd
import os
```

These are already imported at the top of the file (lines 9, and would need to add pandas).

### Fix:
Add `import pandas as pd` at the top of app.py (if not already there), then remove from function.

---

## Issue 2: Excessive Debug Print Statements

### Example 1: Lines 309-356 in yeni_ariza_bildir() GET handler

**Current:**
```python
print(f"\n📥 GET /yeni-ariza-bildir - FRACAS ID hesaplanıyor...")
print(f"   📁 Dosya: {ariza_listesi_file}")
print(f"   ✓ Var mı: {os.path.exists(ariza_listesi_file)}")
# ... 10+ more print statements
```

**Should be replaced with:**
```python
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Calculating FRACAS ID from {ariza_listesi_file}")
logger.debug(f"File exists: {os.path.exists(ariza_listesi_file)}")
```

### Example 2: Lines 1658-1668 - System loading debug output

**Current:**
```python
print(f"\n{'='*60}")
print(f"EXCEL'DEN ÇEKILEN SİSTEMLER:")
print(f"{'='*60}")
print(f"Toplam Sistem Sayısı: {len(sistemler)}")
for sistem_adi, data in sistemler.items():
    print(f"\n📌 {sistem_adi}")
    if data.get('tedarikçiler'):
        print(f"   Tedarikçiler: {', '.join(data['tedarikçiler'])}")
    if data.get('alt_sistemler'):
        print(f"   Alt Sistemler: {', '.join(data['alt_sistemler'])}")
print(f"{'='*60}\n")
```

**Should be:**
```python
logger.debug(f"Loaded {len(sistemler)} systems from Excel")
for sistem_adi, data in sistemler.items():
    suppliers = ', '.join(data.get('tedarikçiler', []))
    subsystems = ', '.join(data.get('alt_sistemler', []))
    logger.debug(f"{sistem_adi}: suppliers={suppliers}, subsystems={subsystems}")
```

---

## Issue 3: Code Duplication - Excel File Loading

Excel file loading appears in 5 locations:

### Location 1: Lines ~367-410 in yeni_ariza_bildir()
```python
veriler_path = None
if os.path.exists(data_dir):
    for file in os.listdir(data_dir):
        if 'veriler' in file.lower() and file.endswith('.xlsx'):
            veriler_path = os.path.join(data_dir, file)
            break

if veriler_path and os.path.exists(veriler_path):
    try:
        wb = load_workbook(veriler_path)
        ws = wb['Sayfa1']
        # ... processing
```

### Location 2: Lines ~1560-1610 in servis_durumu()
```python
excel_path = None
project = session.get('current_project', 'belgrad')
data_dir = os.path.join(os.path.dirname(__file__), 'data', project)

if os.path.exists(data_dir):
    for file in os.listdir(data_dir):
        if file.endswith('.xlsx') and 'Veriler' in file:
            excel_path = os.path.join(data_dir, file)
            break
```

### Solution: Create utils.py with helper functions

**New file: utils.py**
```python
"""Utility functions for app.py"""
import os
from openpyxl import load_workbook

def find_excel_file(directory, filename_pattern, extensions=('.xlsx', '.xls')):
    """Find first Excel file matching pattern in directory"""
    if not os.path.exists(directory):
        return None
    
    for file in os.listdir(directory):
        if filename_pattern.lower() in file.lower() and file.endswith(extensions):
            return os.path.join(directory, file)
    return None

def load_excel_sheet(filepath, sheet_name='Sayfa1'):
    """Load Excel sheet and return worksheet"""
    try:
        wb = load_workbook(filepath)
        if sheet_name in wb.sheetnames:
            return wb[sheet_name], wb
        elif len(wb.sheetnames) > 0:
            return wb[wb.sheetnames[0]], wb
    except Exception as e:
        logger.error(f"Error loading Excel {filepath}: {e}")
    return None, None

def get_project_data_dir(root_path, project_code):
    """Get data directory for project"""
    return os.path.join(root_path, 'data', project_code)
```

Then in app.py, replace all those sections with:
```python
from utils import find_excel_file, load_excel_sheet, get_project_data_dir

# Replace 20+ lines of duplication with:
data_dir = get_project_data_dir(app.root_path, project_code)
veriler_path = find_excel_file(data_dir, 'veriler')

if veriler_path:
    ws, wb = load_excel_sheet(veriler_path, 'Sayfa1')
    if ws:
        # Process worksheet
```

---

## Issue 4: Long Function: yeni_ariza_bildir() - 730 Lines

### Current Structure (Lines 293-730):
- GET handler: Load form data, system hierarchy, modules, etc.
- POST handler: Save to Excel

### Recommended Refactoring:

**Extract to helper functions:**

```python
def _get_next_fracas_id(ariza_listesi_file):
    """Calculate next FRACAS ID from existing file"""
    # Lines 510-545
    pass

def _load_system_hierarchy(veriler_path):
    """Load system hierarchy from Veriler.xlsx"""
    # Lines 367-410
    pass

def _load_form_options(data_dir):
    """Load tramvaylar, modules, classes, etc from Veriler.xlsx"""
    # Lines 420-481
    pass

def _save_ariza_to_excel(ariza_listesi_file, form_data, next_fracas_id):
    """Save failure report to Excel file"""
    # Lines 550-718
    pass

# Then yeni_ariza_bildir() becomes:
@app.route('/yeni-ariza-bildir', methods=['GET', 'POST'])
@login_required
def yeni_ariza_bildir():
    project = session.get('current_project', 'belgrad')
    data_dir = os.path.join(os.path.dirname(__file__), 'data', project)
    
    if request.method == 'GET':
        system_hierarchy = _load_system_hierarchy(data_dir)
        form_options = _load_form_options(data_dir)
        next_fracas_id = _get_next_fracas_id(...)
        
        return render_template('yeni_ariza_bildir.html',
                             sistem_detay=system_hierarchy,
                             next_fracas_id=next_fracas_id,
                             **form_options)
    else:  # POST
        form_data = request.form.to_dict()
        next_fracas_id = _get_next_fracas_id(...)
        try:
            _save_ariza_to_excel(ariza_listesi_file, form_data, next_fracas_id)
            flash('Arıza başarıyla kaydedildi', 'success')
        except Exception as e:
            flash(f'Kayıt hatası: {str(e)}', 'danger')
        
        return redirect(url_for('yeni_ariza_bildir'))
```

---

## Issue 5: Long Function: servis_durumu() - 290 Lines

### Current Structure (Lines 1521-1810):
- Load tramvays from Excel
- Load system hierarchy
- Calculate statistics
- Load 7-day status matrix
- Prepare data for template

### Recommended Refactoring:

```python
def _load_tramvays_for_project(excel_path):
    """Load tramway list from Veriler.xlsx Sayfa2"""
    # Lines ~1560-1610
    pass

def _calculate_service_stats(today_str):
    """Calculate today's service statistics"""
    # Lines ~1669-1713
    pass

def _load_status_matrix(tram_ids, last_7_days):
    """Load 7-day status matrix from database"""
    # Lines ~1730-1760
    pass

# Then servis_durumu() becomes cleaner:
@app.route('/servis-durumu', methods=['GET', 'POST'])
@login_required
def servis_durumu():
    if request.method == 'POST':
        # Existing POST logic
        pass
    
    # GET method - load data
    project = session.get('current_project', 'belgrad')
    data_dir = get_project_data_dir(app.root_path, project)
    
    excel_path = find_excel_file(data_dir, 'veriler')
    tramvaylar = _load_tramvays_for_project(excel_path) or []
    
    tram_ids = [t.id for t in tramvaylar]
    last_7_days = [...]
    
    sistemler = _load_system_hierarchy(data_dir)
    stats = _calculate_service_stats(datetime.now().strftime('%Y-%m-%d'))
    status_matrix = _load_status_matrix(tram_ids, last_7_days)
    
    return render_template('servis_durumu.html',
                         stats=stats,
                         tramvaylar=tramvaylar,
                         sistemler=sistemler,
                         status_matrix=status_matrix)
```

---

## Issue 6: TODO Comment to Remove

### Line 792:
```python
# TODO: Buraya işlem kodunuzu ekleyebilirsiniz
```

This is in the `/ariza-listesi-veriler/process` route. Either:
1. Remove if not needed
2. Implement the functionality
3. Replace with actual code comment explaining what should happen

**Recommendation:** This route appears incomplete. Either implement or remove the route entirely.

---

## Summary of Refactoring Benefits

| Issue | Current | After Refactor | Benefit |
|-------|---------|----------------|---------|
| Print statements | 60+ | 0 | Proper logging, cleaner output |
| Duplicate Excel loading | 5 places | 1 utils function | DRY principle, maintainability |
| Long functions | 730 + 290 lines | 200-250 lines each | Easier to test, understand, maintain |
| Code duplication | High | Low | Easier to fix bugs in one place |
| Debug output | Excessive | Controlled via logging level | Production ready |

---

## Implementation Steps

1. Create `utils.py` with helper functions
2. Create `logging_config.py` for logging setup
3. Update `app.py` imports
4. Replace duplicate code with utils function calls
5. Extract helper functions from long methods
6. Replace print() with logging calls
7. Test all routes still work
8. Delete test files

---

## Testing After Refactoring

```bash
# Syntax check
python -m py_compile app.py utils.py

# Run app
python app.py

# Test key workflows:
# 1. Login
# 2. Dashboard
# 3. New failure report (/yeni-ariza-bildir)
# 4. Service status (/servis-durumu)
# 5. Failure list (/arizalar)
```

---

**This refactoring will make the codebase more maintainable and production-ready.**
