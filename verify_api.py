"""API'nin gerçek sorunu kontrol et"""
import pandas as pd
import os

fracas_file = r'logs/belgrad/ariza_listesi/Fracas_BELGRAD.xlsx'

print("="*60)
print("[CHECK] FRACAS dosyası veri kontrolü")
print("="*60)

if not os.path.exists(fracas_file):
    print(f"❌ DOSYA BULUNAMAD: {fracas_file}")
    exit(1)

try:
    df = pd.read_excel(fracas_file, sheet_name='FRACAS', header=3)
    print(f"✓ Dosya yüklendi: {len(df)} satır, {len(df.columns)} sütun")
    
    # Sütun adlarını yazdır (ilk çoğun)
    print(f"\nİlk 10 sütun:")
    for i, col in enumerate(df.columns[:10], 1):
        print(f"  {i}. '{col}'")
    
    # API tarafından aranacak sütunları kontrol et
    tram_id_col = None
    for col in df.columns:
        if 'araç' in col.lower() and 'numarası' in col.lower():
            tram_id_col = col
            print(f"\n✓ tram_id sütunu: '{tram_id_col}'")
            break
    
    if not tram_id_col:
        print(f"\n❌ tram_id sütunu BULUNAMAD!")
        print("Bulunan sütunlar:")
        for col in df.columns:
            print(f"  - '{col}'")
        exit(1)
    
    # Arıza sütununu kontrol et
    ariza_col = None
    for col in df.columns:
        if 'arıza sınıfı' in col.lower():
            ariza_col = col
            print(f"✓ Arıza sütunu (sınıfı): '{ariza_col}'")
            break
        if 'arıza tanımı' in col.lower():
            ariza_col = col
            print(f"✓ Arıza sütunu (tanımı): '{ariza_col}'")
            break
    
    if not ariza_col:
        print(f"\n❌ Arıza sütunu BULUNAMAD!")
        exit(1)
    
    # Sistem sütununu kontrol et
    sistem_col = None
    for col in df.columns:
        if col.lower().strip() == 'sistem':
            sistem_col = col
            print(f"✓ Sistem sütunu: '{sistem_col}'")
            break
    
    if not sistem_col:
        print(f"⚠ Sistem sütunu bulunamadı (fallback: Alt Sistem)")
        for col in df.columns:
            if 'alt sistem' in col.lower():
                sistem_col = col
                print(f"✓ Fallback: '{sistem_col}'")
                break
    
    # Arıza dolu satırları kontrol et
    ariza_dolu = df[df[ariza_col].notna()]
    ariza_dolu = ariza_dolu[ariza_dolu[ariza_col] != '']
    ariza_dolu = ariza_dolu[ariza_dolu[ariza_col].astype(str) != 'nan']
    
    print(f"\n✓ Arıza dolu satır: {len(ariza_dolu)}")
    
    # Örnek veri göster
    print(f"\nÖrnek veriler:")
    for idx, row in ariza_dolu.head(3).iterrows():
        tram = row.get(tram_id_col, 'N/A')
        ariza = row.get(ariza_col, 'N/A')[:40]
        sistem = row.get(sistem_col, 'N/A') if sistem_col else 'N/A'
        print(f"  - {tram} ({sistem}): {ariza}...")
    
    print("\n" + "="*60)
    print("✅ SONUÇ: API verileri başarıyla alacak!")
    print("="*60)
    
except Exception as e:
    print(f"❌ HATA: {e}")
    import traceback
    traceback.print_exc()
