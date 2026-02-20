import openpyxl

wb = openpyxl.load_workbook('logs/belgrad/HBR/BOZ-NCR-015_20260219001235.xlsx')
ws = wb.active

print("=" * 70)
print("HBR CHECKBOX KONTROL - BOZ-NCR-015")
print("=" * 70)

cells_to_check = {
    'G9': 'Arıza Sınıfı (Kritik/Yüksek/Orta/Düşük)',
    'G10': 'B - Yüksek',
    'G11': 'C - Orta/Düşük',
    'H9': 'İlk Defa Karşılaşılan Arıza',
    'A12': 'Tekrarlayan aynı araçta',
    'E12': 'Tekrarlayan farklı araçlarda'
}

for cell_ref, description in cells_to_check.items():
    cell = ws[cell_ref]
    value = cell.value if cell.value else "(boş)"
    
    # Check if merged
    is_merged = False
    for merged_range in ws.merged_cells.ranges:
        if cell_ref in merged_range:
            is_merged = True
            break
    
    merged_text = " [MERGED]" if is_merged else ""
    checkbox_present = "☑" in str(value)
    checkbox_status = "✅ VAR" if checkbox_present else "❌ YOK"
    
    print(f"\n✓ {cell_ref} ({description}):")
    print(f"   İçerik: {str(value)[:80]}")
    print(f"   Checkbox: {checkbox_status}{merged_text}")
