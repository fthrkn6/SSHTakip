import openpyxl
import os

excel_file = r'logs\ariza_listesi\Ariza_Listesi_BELGRAD.xlsx'
if os.path.exists(excel_file):
    wb = openpyxl.load_workbook(excel_file)
    ws = wb['Ariza Listesi']
    
    # Add sample Personnel Count data to first 5 data rows
    sample_data = [2, 1, 3, 2, 1]  # Sample personnel counts
    
    for idx, personnel_count in enumerate(sample_data, start=5):  # Start from row 5
        ws.cell(idx, 30).value = personnel_count
    
    # Save the file
    wb.save(excel_file)
    wb.close()
    print(f"✅ Personnel Count verileri eklendi: {len(sample_data)} satırda")
    print("Personel Sayısı: 2, 1, 3, 2, 1")
else:
    print('❌ Excel dosyası bulunamadı')
