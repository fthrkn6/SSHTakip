# CLEANUP EXECUTION CHECKLIST

Use this checklist to track cleanup progress. Print and mark items as you complete them.

---

## PHASE 1: SAFE FILE DELETION ⏱️ ~15 minutes

### Step 1.1: Obsolete App Files
- [ ] Verify old_app.py is not referenced anywhere
- [ ] Verify app_broken.py is not referenced anywhere
- [ ] Delete old_app.py
- [ ] Delete app_broken.py
- [ ] Delete app_broken_backup.py
- [ ] Delete app_3commits_ago.py
- [ ] Git add (for deletion)

### Step 1.2: Test Files (33 files)
- [ ] Verify no active references to test_*.py files
- [ ] Delete all test_*.py files in bulk
```
test_fracas_id.py
test_fracas_page.py
test_fracas_analysis.py
test_integration_fracas.py
test_get_excel.py
test_get_excel_path.py
test_excel_read.py
test_excel_display.py
test_excel_fix.py
test_load.py
test_export_debug.py
test_export_simple.py
test_export_validation.py
test_exports_direct.py
test_render.py
test_json_render.py
test_route_direct.py
test_session_path.py
test_id.py
test_http.py
test_count_records.py
test_create_app_simple.py
test_debug.py
test_report_content.py
test_service_status_data.py
test_arizalar.py
test_arizalar_client.py
test_arizalar_debug.py
test_arizalar_endpoint.py
test_ariza_data.py
test_buttons.py
test_form.py
test_app.py
```

## Debug & Analysis Scripts
```
debug_ariza_listesi.py
debug_excel.py
debug_template.html (in templates/)
analyze_equipment_sources.py
analyze_excel.py
analyze_excel_rows.py
analyze_html_detail.py
ANALYSIS_FAILURE_REPORT.py
```

## Temporary Utility Scripts (RECOMMENDED FOR DELETE)
```
add_test_data.py
add_tramvays.py
create_belgrad_test_data.py
create_sample_data.py
create_categorized_excel.py
create_failure_list_excel.py
create_service_test_data.py
delete_test_equipment.py
check_belgrad_data.py
check_columns.py
check_data.py
check_db_data.py
check_excel_costs.py
check_excel_headers.py
check_excel_sheets.py
check_excel_tram_ids.py
check_excel.py
check_fracas.py
check_headers.py
check_html.py
check_metrics.py
check_projects.py
check_sheets.py
check_sistemler.py
check_veriler_bel.py
check_veriler_excel.py
extract_ids.py
fix_equipment_names.py
fix_equipment_names_all.py
fix_headers.py
fix_template.py
categorize_by_color.py
apply_zebra_pattern.py
verify_belgrad_data.py
ask_choice.py
hierarchical_structure.py
load_sistemler_structure.py
quick_check.py
sync_fracas_data.py
update_excel_headers.py
export_ariza_listesi.py
```

## Files to ARCHIVE (Keep for reference, mark deprecated)
```
setup_admin.py
init_db.py
init_service_status.py
add_missing_equipment.py
```

## Template Files to Delete
```
templates/servis_durumu_backup.html
templates/servis_durumu_enhanced.html
```

## Optional: Config Files to Delete (if not used)
```
config_cmms.py
models_cmms.py
requirements_cmms.txt
```

---

## app.py - Print Statements to Remove/Replace (Lines)

Replace with logging module:
- Line 38
- Line 148
- Line 226
- Lines 309, 317, 318, 327, 337, 343, 346, 348, 351, 356
- Line 410
- Lines 423, 444, 452, 460, 468, 478, 481
- Lines 498, 499, 503
- Lines 530, 538, 543, 545, 550
- Lines 627, 654, 718
- Lines 762, 765, 796, 799
- Line 867
- Line 997
- Line 1306
- Line 1581
- Line 1653
- Lines 1658-1668 (large debug output block)
- Lines 1705-1710
- Line 1713
- Line 1882
- Lines 1919-1921
- Line 1925
- Line 1951
- Lines 1958-1960

---

## PowerShell Script to Delete Files

```powershell
# Change to project directory
cd 'c:\Users\ferki\Desktop\bozankaya_ssh_takip'

# Delete obsolete app files
Remove-Item -Force -Confirm old_app.py, app_broken.py, app_broken_backup.py, app_3commits_ago.py

# Delete all test files
Remove-Item -Force -Confirm test_*.py

# Delete debug files
Remove-Item -Force -Confirm debug_*.py, analyze_*.py

# Delete temporary scripts (be careful - review before deleting)
Remove-Item -Force -Confirm add_test_data.py, add_tramvays.py, create_*.py, delete_test_equipment.py
Remove-Item -Force -Confirm check_*.py, extract_ids.py, fix_*.py
Remove-Item -Force -Confirm categorize_by_color.py, apply_zebra_pattern.py, verify_*.py
Remove-Item -Force -Confirm ask_choice.py, hierarchical_structure.py, load_sistemler_structure.py
Remove-Item -Force -Confirm quick_check.py, sync_fracas_data.py, update_excel_headers.py
Remove-Item -Force -Confirm export_ariza_listesi.py

# Delete template backups
Remove-Item -Force -Confirm templates\servis_durumu_backup.html, templates\servis_durumu_enhanced.html

# Optional: Delete config files if not used
# Remove-Item -Force -Confirm config_cmms.py, models_cmms.py, requirements_cmms.txt

Write-Host "Cleanup complete!" -ForegroundColor Green
```

---

## Verify After Cleanup

1. Check app.py syntax: `python -m py_compile app.py`
2. Start app: `python app.py`
3. Verify no import errors in logs
4. Test key routes in browser
5. Run any existing integration tests

---

**Total cleanup: 50+ files, ~100 lines of code to refactor**
