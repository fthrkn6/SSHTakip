#!/usr/bin/env python3
"""Test - Basit text tabloları ile rapor"""

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from datetime import datetime

buffer = BytesIO()
doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.7*cm)
story = []

styles = getSampleStyleSheet()

# Title style
title_style = ParagraphStyle(
    'Title', parent=styles['Heading1'], fontSize=18,
    textColor=colors.white, alignment=TA_CENTER
)

# Data style
data_style = ParagraphStyle(
    'Data', parent=styles['Normal'], fontSize=9,
    textColor=colors.HexColor('#333'), alignment=TA_LEFT
)

print("[1] Basit text tabloları ile rapor oluşturuluyor...")

# Başlık
story.append(Paragraph("YONETIM RAPORU - BELGRAD", title_style))
story.append(Spacer(1, 0.3*cm))

# Info
story.append(Paragraph(f"Periyot: AYLIK (Mart 2026) | {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
story.append(Spacer(1, 0.3*cm))

# KPI Summary
story.append(Paragraph("<b>KPI OZETI:</b>", styles['Heading2']))
story.append(Paragraph("Araclar: 4 | Sistemler: 6 | Downtime Ort: 2.5 saat | MTBF Ort: 33 km", styles['Normal']))
story.append(Spacer(1, 0.25*cm))

# Araç analizi - text halinde
story.append(Paragraph("<b>1. ARAC BAZINDA ANALIZ</b>", styles['Heading3']))

vehicle_data = [
    ("1532.0", "100", "3", "33", "96.5%"),
    ("1541.0", "2500", "5", "500", "95.0%"),
    ("1555.0", "15000", "12", "1250", "91.0%"),
    ("1560.0", "5000", "2", "2500", "97.0%"),
]

# Başlık satırı
header = f"<b>{'Araç No':12s} {'KM':12s} {'Arıza':8s} {'MTBF':10s} {'Avail':8s}</b>"
story.append(Paragraph(header, data_style))

# Veri satırları
for vehicle, km, failure, mtbf, avail in vehicle_data:
    line = f"{vehicle:12s} {km:>12s} {failure:>8s} {mtbf:>10s} {avail:>8s}"
    story.append(Paragraph(line, data_style))

story.append(Spacer(1, 0.2*cm))

# Sistem analizi
story.append(Paragraph("<b>2. SISTEM BAZINDA ANALIZ</b>", styles['Heading3']))

system_data = [
    ("Traction_Converter", "3", "37.5%", "0.0"),
    ("Door_System", "2", "25.0%", "5.0"),
    ("HVAC_System", "1", "12.5%", "0.0"),
    ("Brake_System", "1", "12.5%", "0.0"),
    ("Electrical_System", "1", "12.5%", "0.0"),
]

header = f"<b>{'Sistem':20s} {'Arıza':8s} {'Yuzde':10s} {'Downtime':10s}</b>"
story.append(Paragraph(header, data_style))

for sistem, count, pct, downtime in system_data:
    line = f"{sistem:20s} {count:>8s} {pct:>10s} {downtime:>10s} saat"
    story.append(Paragraph(line, data_style))

story.append(Spacer(1, 0.2*cm))

# Tedarikçi-Sistem
story.append(Paragraph("<b>3. TEDARIKCI-SISTEM MATRISI</b>", styles['Heading3']))

matrix_data = [
    ("Traction_Converter", "Medcom: 3"),
    ("Door_System", "Kalite: 1L, NSC Tek: 1"),
    ("HVAC_System", "Klimasys: 1"),
]

for sistem, suppliers in matrix_data:
    line = f"{sistem}: {suppliers}"
    story.append(Paragraph(line, data_style))

print("[2] PDF oluşturuluyor...")

try:
    doc.build(story)
    buffer.seek(0)
    pdf_content = buffer.getvalue()
    
    with open('test_simple_text_rapor.pdf', 'wb') as f:
        f.write(pdf_content)
    
    print(f"✓ PDF başarıyla oluşturuldu: test_simple_text_rapor.pdf ({len(pdf_content)} bytes)")
    print("\n✓ Tabloların text versiyonları PDF'e başarıyla eklendi!")
    
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
