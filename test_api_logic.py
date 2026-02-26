"""API fonksiyonunu direkt test et - login gerekmiyor"""
import pandas as pd
import os

def test_api(equipment_code=None):
    """API logikini direkt test et"""
    current_project = 'belgrad'
    
    # Excel'den arızaları oku
    veriler_file = os.path.join('data', current_project, 'Veriler.xlsx')
    
    if not os.path.exists(veriler_file):
        print(f'[ERROR] {veriler_file} bulunamadi')
        return
    
    try:
        df = pd.read_excel(veriler_file, sheet_name='Sayfa2', header=0)
        print(f'[OK] Excel okundu - {len(df)} satir\n')
        
        # Arıza sütununu bul
        ariza_col = None
        for col in df.columns:
            if 'arız' in col.lower() or 'class' in col.lower():
                ariza_col = col
                break
        
        # Önce arıza dolu satırları filtrele
        if ariza_col:
            filtered_df = df[df[ariza_col].notna()]
            filtered_df = filtered_df[filtered_df[ariza_col] != '']
            filtered_df = filtered_df[filtered_df[ariza_col] != 'nan']
            print(f'[OK] Arıza dolu satırlar: {len(filtered_df)}\n')
        else:
            filtered_df = df
        
        # Equipment code verilirse filtrele
        if equipment_code:
            equipment_code = equipment_code.strip().replace('TRN-', '')
            print(f'[FILTER] Araç: {equipment_code}\n')
            
            # tram_id kolonunu bul ve normal et
            tram_id_col = 'tram_id'  # Biliyoruz ki bu var
            
            # String'e çevir ve normalize et
            filtered_df[tram_id_col] = filtered_df[tram_id_col].astype(str).str.strip()
            filtered_df[tram_id_col] = filtered_df[tram_id_col].apply(
                lambda x: str(int(float(x))) if x.replace('.', '').replace(',', '').isdigit() else x
            )
            filtered_df = filtered_df[filtered_df[tram_id_col] == equipment_code]
            print(f'[OK] {equipment_code} için {len(filtered_df)} arıza bulundu\n')
        else:
            print(f'[GLOBAL] Tüm arızalar\n')
        
        # Son 5 arızayı al
        filtered_df = filtered_df.tail(5)
        
        failures = []
        for idx, row in filtered_df.iterrows():
            try:
                tram_id = str(row.get('tram_id', '')).strip()
                
                # tram_id'yi normalize et (1547.0 -> 1547)
                if tram_id and tram_id != 'nan':
                    try:
                        tram_id = str(int(float(tram_id)))
                    except:
                        pass
                
                # Module/Sistem
                module = str(row.get('Module', '')).strip()
                if not module or module == 'nan':
                    module = 'Bilinmiyor'
                
                # Arıza Sınıfı
                ariza_sinifi = str(row.get('Arıza Sınıfı ', '')).strip()
                
                # NaN değerleri filtrele
                if not ariza_sinifi or ariza_sinifi == 'nan':
                    print(f'[SKIP] Boş arıza satırı')
                    continue
                
                # Arıza Kaynağı ve Tipi
                ariza_kaynagi = str(row.get('Arıza Kaynağı', '')).strip() if 'Arıza Kaynağı' in row.index else ''
                ariza_tipi = str(row.get('Arıza Tipi', '')).strip() if 'Arıza Tipi' in row.index else ''
                
                failures.append({
                    'fracas_id': tram_id,
                    'arac_no': tram_id,
                    'sistem': module,
                    'ariza_tanimi': ariza_sinifi,
                    'tarih': '',
                    'durum': f'{ariza_kaynagi} | {ariza_tipi}' if ariza_kaynagi else ariza_tipi
                })
            except Exception as e:
                print(f'[ERROR] Satır işleme hatası: {e}')
                continue
        
        return failures
    
    except Exception as e:
        print(f'[ERROR] {e}')
        import traceback
        traceback.print_exc()
        return []

# Test 1: Global
print("="*60)
print("[TEST 1] Global - Son 5 arıza")
print("="*60)
results = test_api()
for f in results:
    print(f"✓ {f['fracas_id']} ({f['sistem']}): {f['ariza_tanimi']}")
print(f"Toplam: {len(results)}\n")

# Test 2: 1531 için
print("="*60)
print("[TEST 2] 1531 araçı")
print("="*60)
results = test_api('1531')
for f in results:
    print(f"✓ {f['fracas_id']} ({f['sistem']}): {f['ariza_tanimi']}")
print(f"Toplam: {len(results)}\n")

# Test 3: 1532 için
print("="*60)
print("[TEST 3] 1532 araçı")
print("="*60)
results = test_api('1532')
for f in results:
    print(f"✓ {f['fracas_id']} ({f['sistem']}): {f['ariza_tanimi']}")
print(f"Toplam: {len(results)}\n")
