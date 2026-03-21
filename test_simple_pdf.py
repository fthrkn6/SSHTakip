#!/usr/bin/env python3
"""Basit test PDF - Tablo oluşturmayı test et"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

buffer = BytesIO()
doc = SimpleDocTemplate(buffer, pagesize=A4)
story = []

styles = getSampleStyleSheet()

print("[1] PDF inşa ediliyor...")

# Başlık
title = Paragraph("<b>BASIT TEST RAPORU</b>", styles['Heading1'])
story.append(title)
story.append(Spacer(1, 0.5*cm))

# Metin
story.append(Paragraph("Bu basit bir test raporudur.", styles['Normal']))
story.append(Spacer(1, 0.3*cm))

# Tablo
table_data = [
    ['Araç Numarası', 'KM', 'Arıza Sayısı'],
    ['1532', '100', '3'],
    ['1541', '2500', '5'],
    ['1555', '15000', '12']
]

try:
    print("  [2] Tablo oluşturuluyor...")
    table = Table(table_data, colWidths=[5*cm, 3*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ddd')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
    ]))
    story.append(table)
    print("  ✓ Tablo başarıyla oluşturuldu")
except Exception as e:
    print(f"  ✗ Tablo oluşturma hatası: {e}")
    import traceback
    traceback.print_exc()

story.append(Spacer(1, 0.3*cm))

# Metin
story.append(Paragraph("Test başarılı ise tablonun üzerinde görünecek.", styles['Normal']))

print("[3] PDF yazılıyor...")
try:
    doc.build(story)
    buffer.seek(0)
    pdf_content = buffer.getvalue()
    
    with open('test_simple_table.pdf', 'wb') as f:
        f.write(pdf_content)
    
    print(f"✓ PDF oluşturuldu: test_simple_table.pdf ({len(pdf_content)} bytes)")
    
    # PDF'de tablo metni var mı kontrol et
    if b'Ara' in pdf_content or b'1532' in pdf_content:
        print("✓ PDF'de tablo verisi bulundu!")
    else:
        print("[!] PDF'de tablo verisi bulunamadı")
except Exception as e:
    print(f"✗ PDF yazma hatası: {e}")
    import traceback
    traceback.print_exc()
