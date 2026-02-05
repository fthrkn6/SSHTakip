# Code Cleanup Analysis Report
**Bozankaya SSH Takip Project**  
**Date:** February 5, 2026

---

## EXECUTIVE SUMMARY

This project contains **significant dead code and obsolete files** that should be removed. Analysis identified:
- **28 test files** (mostly for debugging specific features)
- **3 broken/old app files** (backups and version snapshots)
- **8 debug/analysis scripts** (for troubleshooting)
- **Excessive debug print statements** throughout app.py
- **Unused imports** in several files
- **Commented-out code blocks**

**Total files to clean: 50+**

---

## 1. FILES TO DELETE

### 1.1 Obsolete Application Files (DELETE)

| File | Reason |
|------|--------|
| [old_app.py](old_app.py) | Completely superseded by app.py. Contains old implementation. |
| [app_broken.py](app_broken.py) | Broken/non-functional version with disabled routes. Contains debug comments. |
| [app_broken_backup.py](app_broken_backup.py) | Backup of broken version. Has commented-out app variable. |
| [app_3commits_ago.py](app_3commits_ago.py) | Historical backup from 3 commits ago. Unused version snapshot. |

### 1.2 Test/Debug Scripts for Individual Features (DELETE - 28 files)

All of these are one-off test files for debugging specific functionality. They are NOT integration tests and serve no purpose in production or ongoing development:

**FRACAS Testing:**
- [test_fracas_id.py](test_fracas_id.py) - FRACAS ID calculation test
- [test_fracas_page.py](test_fracas_page.py) - FRACAS page rendering test
- [test_fracas_analysis.py](test_fracas_analysis.py) - FRACAS analysis test
- [test_integration_fracas.py](test_integration_fracas.py) - FRACAS integration test

**Excel/Data Testing:**
- [test_get_excel.py](test_get_excel.py) - Excel path retrieval test
- [test_get_excel_path.py](test_get_excel_path.py) - Excel path test
- [test_excel_read.py](test_excel_read.py) - Excel reading test
- [test_excel_display.py](test_excel_display.py) - Excel display test
- [test_excel_fix.py](test_excel_fix.py) - Excel fixing test
- [test_load.py](test_load.py) - Data loading test

**Export/Report Testing:**
- [test_export_debug.py](test_export_debug.py) - Export debugging test
- [test_export_simple.py](test_export_simple.py) - Simple export test
- [test_export_validation.py](test_export_validation.py) - Export validation test
- [test_exports_direct.py](test_exports_direct.py) - Direct export test

**Rendering/JSON Testing:**
- [test_render.py](test_render.py) - Template rendering test
- [test_json_render.py](test_json_render.py) - JSON rendering test
- [test_route_direct.py](test_route_direct.py) - Route direct test

**Data Testing:**
- [test_session_path.py](test_session_path.py) - Session path test
- [test_id.py](test_id.py) - ID calculation test
- [test_http.py](test_http.py) - HTTP request test
- [test_count_records.py](test_count_records.py) - Record counting test
- [test_create_app_simple.py](test_create_app_simple.py) - Simple app creation test
- [test_debug.py](test_debug.py) - General debug test
- [test_report_content.py](test_report_content.py) - Report content test
- [test_service_status_data.py](test_service_status_data.py) - Service status data test
- [test_arizalar.py](test_arizalar.py) - Failures list test
- [test_arizalar_client.py](test_arizalar_client.py) - Failures client test
- [test_arizalar_debug.py](test_arizalar_debug.py) - Failures debug test
- [test_arizalar_endpoint.py](test_arizalar_endpoint.py) - Failures endpoint test
- [test_ariza_data.py](test_ariza_data.py) - Failure data test
- [test_buttons.py](test_buttons.py) - Button functionality test
- [test_form.py](test_form.py) - Form test
- [test_app.py](test_app.py) - General app test

### 1.3 Debug & Analysis Scripts (DELETE - 8 files)

| File | Reason |
|------|--------|
| [debug_ariza_listesi.py](debug_ariza_listesi.py) | Debug script for failure list - temporary debugging |
| [debug_excel.py](debug_excel.py) | Debug script for Excel reading - temporary debugging |
| [debug_template.html](debug_template.html) | Debug HTML template file - unused |
| [analyze_equipment_sources.py](analyze_equipment_sources.py) | One-off analysis of equipment sources |
| [analyze_excel.py](analyze_excel.py) | One-off Excel analysis |
| [analyze_excel_rows.py](analyze_excel_rows.py) | One-off Excel row analysis |
| [analyze_html_detail.py](analyze_html_detail.py) | One-off HTML detail analysis |
| [ANALYSIS_FAILURE_REPORT.py](ANALYSIS_FAILURE_REPORT.py) | One-off failure report analysis |

### 1.4 Temporary Test Data & Utility Scripts (DELETE - Optional but recommended)

| File | Reason | Recommendation |
|------|--------|---|
| [add_test_data.py](add_test_data.py) | Temporary test data creation | DELETE - Use proper migration scripts instead |
| [add_tramvays.py](add_tramvays.py) | Temporary tramway data | DELETE |
| [add_missing_equipment.py](add_missing_equipment.py) | One-time equipment sync | ARCHIVE (keep for reference, mark as deprecated) |
| [create_belgrad_test_data.py](create_belgrad_test_data.py) | Test data for Belgrad | DELETE or ARCHIVE |
| [create_sample_data.py](create_sample_data.py) | Sample data creation | DELETE |
| [create_categorized_excel.py](create_categorized_excel.py) | Excel categorization utility | DELETE if not used |
| [create_failure_list_excel.py](create_failure_list_excel.py) | Failure list generation | DELETE if not used |
| [create_service_test_data.py](create_service_test_data.py) | Service test data | DELETE |
| [delete_test_equipment.py](delete_test_equipment.py) | Delete test equipment | DELETE (use database migration instead) |
| [check_*.py](check_*.py) - Multiple files (12 files) | Various data validation checks | DELETE - should be in testing framework |
| [extract_ids.py](extract_ids.py) | ID extraction utility | DELETE if not used |
| [fix_*.py](fix_*.py) - 3 files | Temporary data fixing scripts | DELETE (fixes should be applied, scripts removed) |
| [categorize_by_color.py](categorize_by_color.py) | Categorization by color | DELETE |
| [apply_zebra_pattern.py](apply_zebra_pattern.py) | Excel styling utility | DELETE |
| [verify_belgrad_data.py](verify_belgrad_data.py) | Belgrad data verification | DELETE |
| [ask_choice.py](ask_choice.py) | User choice utility | DELETE |
| [hierarchical_structure.py](hierarchical_structure.py) | Structure analysis | DELETE |
| [load_sistemler_structure.py](load_sistemler_structure.py) | System structure loading | DELETE |
| [quick_check.py](quick_check.py) | Quick check utility | DELETE |
| [sync_fracas_data.py](sync_fracas_data.py) | FRACAS data sync | DELETE if not used in automation |
| [update_excel_headers.py](update_excel_headers.py) | Excel header update | DELETE |
| [export_ariza_listesi.py](export_ariza_listesi.py) | Failure list export | DELETE - use built-in export routes |
| [setup_admin.py](setup_admin.py) | Admin setup script | ARCHIVE (keep for reference, mark as deprecated) |
| [init_db.py](init_db.py) | Database initialization | ARCHIVE (keep for initial setup reference) |
| [init_service_status.py](init_service_status.py) | Service status initialization | ARCHIVE (keep for reference) |
| [migrate_db.py](migrate_db.py) | Database migration | KEEP (but review for obsolete code) |
| [config.py](config.py) | Configuration file | REVIEW (check if all settings are used) |
| [config_cmms.py](config_cmms.py) | CMMS configuration | DELETE if not used |
| [models_cmms.py](models_cmms.py) | CMMS models | DELETE if not used |
| [requirements_cmms.txt](requirements_cmms.txt) | CMMS requirements | DELETE if not used |
| [utils_availability.py](utils_availability.py) | Availability utilities | REVIEW - check if used |
| [utils_service_status.py](utils_service_status.py) | Service status utilities | REVIEW - check if used |

---

## 2. app.py CLEANUP

### 2.1 Remove Debug Print Statements

**Lines to remove or replace with logging:**

| Line Range | Content | Action |
|-----------|---------|--------|
| 38 | `print('create_app started')` | REMOVE - use logging |
| 148 | `print(f"Excel okuma hatası: {e}")` | REPLACE with logging.error() |
| 226 | `print(f"Veriler.xlsx okuma hatası: {e}")` | REPLACE with logging.error() |
| 309-356 | Multiple print statements in `/yeni-ariza-bildir` GET | REMOVE - excessive debug output |
| 410 | `print(f"Sistem yükleme hatası: {e}")` | REPLACE with logging.error() |
| 423, 444, 452, 460, 468, 478, 481 | Debug comments in Veriler.xlsx loading | REMOVE - excessive print statements |
| 498-550 | Multiple print statements in POST handler | REMOVE - excessive debug output |
| 627, 654, 718 | Print statements in Excel writing | REPLACE with logging |
| 762, 765, 796, 799 | Print statements in ariza_listesi handlers | REPLACE with logging |
| 867 | `print(f"Parts lookup hatası: {e}")` | REPLACE with logging.error() |
| 997 | `print(f"Excel okuma hatası: {e}")` | REPLACE with logging.error() |
| 1306 | `print(f"Excel okuma hatası: {str(e)}")` | REPLACE with logging.error() |
| 1581 | `print(f"Excel okuşta hata: {e}")` | REPLACE with logging.error() |
| 1653 | `print(f"Sistem verileri yüklenirken hata: {e}")` | REPLACE with logging.error() |
| 1658-1668 | Print statements for system data debugging | REMOVE or move to logging.debug() |
| 1705-1710 | Statistics print statements | REMOVE or move to logging.debug() |
| 1713 | `print(f"ServiceStatus hatası: {e}\n")` | REPLACE with logging.error() |
| 1882 | `print(f"Hata: {e}")` | REPLACE with logging.error() |
| 1919-1921 | App creation debug prints | REMOVE - use logging |
| 1925 | Critical error print | REPLACE with logging.critical() |
| 1951 | Sample data initialization print | REMOVE or move to logging.info() |
| 1958-1960 | Startup information prints | MOVE to logging.info() |

**Total: 60+ print statements to clean up**

### 2.2 Remove TODO/FIXME Comments

| Line | Content | Action |
|------|---------|--------|
| 792 | `# TODO: Buraya işlem kodunuzu ekleyebilirsiniz` | REMOVE - comment serves no purpose |

### 2.3 Remove Unused Imports

**Analysis Result:** All imports appear to be used:
- `datetime` - used throughout
- `secure_filename` - used for file uploads
- `get_excel_path, get_column` - used in routes
- `os, shutil, tempfile` - used for file operations

**No unused imports to remove.**

### 2.4 Remove Unnecessary Code Blocks

**Function: `dashboard()` (Lines ~117-250)**
- Lines 217-226: Duplicate `import pandas` and `import os` (already imported at top)
- **Action:** Extract to single import statement at top of file

**Function: `yeni_ariza_bildir()` (Lines ~293-730)**
- Extremely long function with inline imports and comments
- **Recommendation:** Refactor into separate helper functions:
  - `calculate_next_fracas_id()`
  - `load_system_hierarchy()`
  - `save_ariza_to_excel()`
  - `load_form_data()`

**Function: `servis_durumu()` (Lines ~1521-1810)**
- Very long function (290 lines)
- Multiple inline imports (pandas, openpyxl)
- Duplicate code for loading Excel files
- **Recommendation:** Extract into helper functions:
  - `load_tramvays_from_excel()`
  - `load_system_hierarchy_from_excel()`
  - `calculate_service_stats()`

### 2.5 Code Quality Issues

**Repeated Code Patterns:**
1. **Excel file loading** (appears in 5 different places):
   - `yeni_ariza_bildir()` - Lines ~360-480
   - `arizalar()` - Lines ~990-1010
   - `servis_durumu()` - Lines ~1560-1610
   - Should be extracted to `utils.py`

2. **System hierarchy loading** (appears in 3 places):
   - `yeni_ariza_bildir()` - Lines ~367-410
   - `servis_durumu()` - Lines ~1630-1655
   - Should be extracted to `utils.py`

3. **Date handling** (appears in multiple places):
   - Should create utility function for date formatting

---

## 3. TEMPLATE CLEANUP

### 3.1 Backup/Unused Templates

| File | Status | Action |
|------|--------|--------|
| [servis_durumu_backup.html](templates/servis_durumu_backup.html) | Backup file | DELETE |
| [servis_durumu_enhanced.html](templates/servis_durumu_enhanced.html) | Alternative version | DELETE (if servis_durumu.html is current) |
| [debug_template.html](debug_template.html) | Debug template | DELETE |

### 3.2 Unused Routes/Templates

Check these templates for actual usage:
- [dokumanlar.html](templates/dokumanlar.html) - Appears unused (no corresponding route in app.py)
- [audit_log.html](templates/audit_log.html) - Route exists at `/audit-log` but seems incomplete

---

## 4. IMPORT CLEANUP ACROSS ALL PYTHON FILES

### Routes Files - Review Imports

**[routes/fracas.py](routes/fracas.py):**
- All imports appear used

**[routes/kpi.py](routes/kpi.py):**
- All imports appear used

**[routes/service_status.py](routes/service_status.py):**
- Review for unused imports (file not shown, but worth checking)

---

## 5. CONFIGURATION FILES TO REVIEW

| File | Issue | Action |
|------|-------|--------|
| [requirements.txt](requirements.txt) | Ensure no test packages in production requirements | REVIEW |
| [requirements_cmms.txt](requirements_cmms.txt) | Appears to be alternative requirements file | DELETE if not used |
| [.env.example](.env.example) | Ensure all vars in use | REVIEW |

---

## 6. COMMENTED-OUT CODE BLOCKS

### In app.py:
- **None found** - Project is well-maintained (no large commented blocks)

### In other files:
- [app_broken_backup.py](app_broken_backup.py) - Lines 3575+: Entire commented app execution section

---

## 7. SUMMARY OF ACTIONS

### IMMEDIATE CLEANUP (High Priority)

1. **Delete 50+ obsolete files:**
   ```
   - old_app.py, app_broken.py, app_broken_backup.py, app_3commits_ago.py
   - All 28 test_*.py files
   - All 8 debug_*.py and analyze_*.py scripts
   - All 20+ temporary utility scripts
   ```

2. **Clean app.py:**
   - Replace 60+ `print()` statements with `logging` module
   - Remove duplicate imports in functions
   - Remove TODO comment at line 792

3. **Delete template backups:**
   - servis_durumu_backup.html
   - servis_durumu_enhanced.html
   - debug_template.html

### MEDIUM PRIORITY

4. **Refactor long functions in app.py:**
   - Break down `yeni_ariza_bildir()` (730 lines)
   - Break down `servis_durumu()` (290 lines)
   - Extract repeated Excel loading logic to utils

5. **Create utils.py file:**
   - Add functions for Excel loading
   - Add functions for system hierarchy loading
   - Add functions for date handling

### LOW PRIORITY

6. **Archive useful historical files:**
   - Keep (but mark as deprecated): `init_db.py`, `setup_admin.py`, `init_service_status.py`
   - These may be useful for documentation/reference

7. **Review configuration:**
   - Verify all imports in requirements.txt are used
   - Clean up alternative config files

---

## 8. ESTIMATED IMPACT

- **Files to delete:** 50+
- **Lines to clean in app.py:** ~100 (print statements)
- **Functions to refactor:** 2 major functions
- **Code duplication:** 3 major patterns to extract
- **Expected code size reduction:** 20-25%
- **Improved maintainability:** High
- **Risk of breaking changes:** Low (only delete, no logic changes)

---

## 9. RECOMMENDED CLEANUP ORDER

1. Delete all test_*.py files (28 files)
2. Delete all old/broken app files (4 files)
3. Delete all debug_*.py and analyze_*.py scripts (8 files)
4. Delete temporary utility scripts (20+ files)
5. Remove all print statements from app.py and replace with logging
6. Delete template backup files (3 files)
7. Extract repeated Excel loading logic to utils.py
8. Refactor long functions in app.py

---

## 10. TESTING AFTER CLEANUP

After cleanup, verify:
- [ ] App starts without errors: `python app.py`
- [ ] All routes work: Test login, dashboard, ariza_bildir, arizalar
- [ ] Excel import/export works: Test FRACAS data import
- [ ] No import errors
- [ ] No missing functionality

---

**End of Report**
