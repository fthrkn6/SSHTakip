"""API logikini FRACAS dosyasıyla test et"""
import pandas as pd
import os

def test_api(equipment_code=None):
    """API logikini direkt test et - FRACAS dosyası kullanarak"""
    current_project = 'belgrad'
    
    # Birincil konum: logs/{project}/ariza_listesi/Fracas_*.xlsx
    ariza_listesi_dir = os.path.join('logs', current_project, 'ariza_listesi')
    
    ariza_listesi_file = None
    use_sheet = None
    header_row = 0
    
    if os.path.exists(ariza_listesi_dir):
        # FRACAS template dosyasını ara
        for file in os.listdir(ariza_listesi_dir):
            if file.upper().startswith('FRACAS_') and file.endswith('.xlsx') and not file.startswith('~$'):
                ariza_listesi_file = os.path.join(ariza_listesi_dir, file)
                use_sheet = 'FRACAS'
                header_row = 3  # FRACAS headers row 4
                break
    
    print(f"Dosya: {ariza_listesi_file}")
    print(f"Sheet: {use_sheet}") 
    print(f"Header row: {header_row}\n")
    
    if not ariza_listesi_file or not os.path.exists(ariza_listesi_file):
        print("[ERROR] Dosya bulunamadı")
        return
    
    try:
        df = pd.read_excel(ariza_listesi_file, sheet_name=use_sheet, header=header_row)
        print(f"[OK] {len(df)} satır okundu\n")
        
        # Sütunları bul
        tram_id_col = None
        for col in df.columns:
            if 'araç' in col.lower() and 'numarası' in col.lower():
                tram_id_col = col
                print(f"✓ tram_id sütunu bulundu: '{col}'")
                break
        
        ariza_col = None
        for col in df.columns:
            if 'arıza sınıfı' in col.lower():
                ariza_col = col
                print(f"✓ Arıza sütunu bulundu: '{col}'")
                break
            if 'arıza tanımı' in col.lower():
                ariza_col = col
                print(f"✓ Arıza sütunu bulundu (tanımı): '{col}'")
                break
        
        sistem_col = None
        for col in df.columns:
            if col.lower().strip() == 'sistem':
                sistem_col = col
                print(f"✓ Sistem sütunu bulundu: '{col}'")
                break
        
        print(f"\nArıza dolu satırları filtrele...")
        filtered_df = df[df[ariza_col].notna()]
        filtered_df = filtered_df[filtered_df[ariza_col] != '']
        filtered_df = filtered_df[filtered_df[ariza_col].astype(str) != 'nan']
        
        print(f"Arıza dolu satır: {len(filtered_df)}\n")
        
        if equipment_code:
            equipment_code = equipment_code.strip()
            print(f"[FILTER] Araç: {equipment_code}")
            
            # tram_id normalize et
            filtered_df[tram_id_col] = filtered_df[tram_id_col].astype(str).str.strip()
            filtered_df[tram_id_col] = filtered_df[tram_id_col].apply(
                lambda x: str(int(float(x))) if x.replace('.', '').isdigit() else x
            )
            filtered_df = filtered_df[filtered_df[tram_id_col] == equipment_code]
            print(f"{equipment_code} araçı: {len(filtered_df)} arıza\n")
        
        # Son 5'ini al
        if len(filtered_df) > 5:
            filtered_df = filtered_df.tail(5)
        
        print(f"Gösterilecek: {len(filtered_df)} arıza\n")
        
        for idx, row in filtered_df.iterrows():
            tram_id = str(row.get(tram_id_col, '')).strip()
            try:
                tram_id = str(int(float(tram_id)))
            except:
                pass
            
            sistem = 'Bilinmiyor'
            if sistem_col:
                sistem = str(row.get(sistem_col, 'Bilinmiyor')).strip()
                if not sistem or sistem == 'nan':
                    sistem = 'Bilinmiyor'
            
            ariza = str(row.get(ariza_col, '')).strip()
            
            print(f"✓ {tram_id} ({sistem}): {ariza[:60]}")
    
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

# Test 1: Global
print("="*60)
print("[TEST 1] Global - Son 5 arıza")
print("="*60)
test_api()

# Test 2: 1531
print("\n" + "="*60)
print("[TEST 2] 1531 araçı")
print("="*60)
test_api('1531')
