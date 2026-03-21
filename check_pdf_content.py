#!/usr/bin/env python3
"""Oluşturulan PDF dosyalarını kontrol et"""
import os

pdf_files = [
    'rapor_test_BELGRAD.pdf',
    'rapor_multi_test.pdf'
]

print("\n" + "="*70)
print("PDF DOSYALARI KONTROL")
print("="*70 + "\n")

for pdf_file in pdf_files:
    if not os.path.exists(pdf_file):
        print(f"✗ {pdf_file} - bulunamadı")
        continue
    
    size = os.path.getsize(pdf_file)
    print(f"✓ {pdf_file} - {size:,d} bytes")
    
    # PDF içeriğini kontrol et
    with open(pdf_file, 'rb') as f:
        content = f.read()
        
        # Tabloların olup olmadığını metin ara
        text_markers = [
            b'Arac',  # Turkish I
            b'Sistem',
            b'BELGRAD',
            b'Yonetim'
        ]
        
        found_markers = []
        for marker in text_markers:
            if marker in content:
                found_markers.append(marker.decode('latin-1', errors='ignore'))
        
        if found_markers:
            print(f"  Bulunanulan metinler: {', '.join(found_markers)}")
        else:
            print(f"  [!] Tablo metni bulunmadı")
    
    print()

print("="*70)
