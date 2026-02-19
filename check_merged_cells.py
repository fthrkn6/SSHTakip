import openpyxl

wb = openpyxl.load_workbook('data/belgrad/FR_010_R06_SSH HBR.xlsx')
ws = wb.active

print("🔍 CHECKBOX HÜCRELERININ MERGED DURUMU:")
print("="*60)

cells = ['G9', 'G10', 'G11', 'H9', 'A12', 'E12']

for cell_ref in cells:
    cell = ws[cell_ref]
    is_merged = False
    merged_range = None
    
    for mr in ws.merged_cells.ranges:
        if cell_ref in mr:
            is_merged = True
            merged_range = str(mr)
            break
    
    status = f"✓ MERGED [{merged_range}]" if is_merged else "✓ NORMAL"
    print(f"\n {cell_ref}:")
    print(f"   Durum: {status}")
    print(f"   Içerik: '{cell.value}'")

print("\n\n" + "="*60)
print("SIZIN HATILADAKILAR (UNMERGE/WRITE/MERGE YAPILAN):")
print("  - G9, G10, G11: Normal hücreler (merged degil)")
print("  - H9: MERGED (H9:K11) - Sorunlu tarafi!")
print("  - A12: MERGED (A12:C14) - Sorunlu tarafi!")  
print("  - E12: MERGED (E12:F14) - Sorunlu tarafi!")
print("\n[ÇÖZÜM] Merged hücreler yazilirken unmerge-write-remerge")
print("        sorunu oldugu icin, boyle hücrelere yazma basarısız olabilir.")
