#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Istanbul için arıza listesi veri kaynağı analizi"""

import os
from pathlib import Path
import pandas as pd

istanbul_data = Path('C:/Users/fatiherkin/Desktop/bozankaya_ssh_takip/data/istanbul')
istanbul_logs = Path('C:/Users/fatiherkin/Desktop/bozankaya_ssh_takip/logs/istanbul/ariza_listesi')

print("\n" + "="*120)
print("ISTANBUL PROJESI - ARIZA LİSTESİ KAYNAĞI ANALIZI".center(120))
print("="*120 + "\n")

# 1. data/ klasöründeki dosyalar
print("[1] data/istanbul/ KLASOERUEUE DOSYALARI:")
print("-" * 120)
if istanbul_data.exists():
    xlsx_files = sorted(istanbul_data.glob('*.xlsx'))
    for file in xlsx_files:
        print(f"\n  {file.name}")
        try:
            xls = pd.ExcelFile(str(file))
            print(f"    Sheet'ler: {', '.join(xls.sheet_names)}")
            
            # FRACAS sheet'ini kontrol et
            if 'FRACAS' in xls.sheet_names:
                df = pd.read_excel(str(file), sheet_name='FRACAS', header=3)
                print(f"    FRACAS Sheet: {len(df)} satir, {len(df.columns)} sutun")
                print(f"    Sutunlar: {', '.join(list(df.columns)[:5])}...")
        except Exception as e:
            print(f"    [Hata] {str(e)[:60]}")

# 2. logs/ klasöründeki dosyalar
print("\n\n[2] logs/istanbul/ariza_listesi/ KLASOERUEUE DOSYALARI:")
print("-" * 120)
if istanbul_logs.exists():
    xlsx_files = sorted(istanbul_logs.glob('*.xlsx'))
    for file in xlsx_files:
        print(f"\n  {file.name}")
        try:
            xls = pd.ExcelFile(str(file))
            print(f"    Sheet'ler: {', '.join(xls.sheet_names)}")
            
            # Ariza Listesi sheet'ini kontrol et
            if 'Ariza Listesi' in xls.sheet_names:
                df = pd.read_excel(str(file), sheet_name='Ariza Listesi', header=3)
                print(f"    Ariza Listesi Sheet: {len(df)} satir, {len(df.columns)} sutun")
            
            # FRACAS sheet'ini kontrol et
            if 'FRACAS' in xls.sheet_names:
                df = pd.read_excel(str(file), sheet_name='FRACAS', header=3)
                print(f"    FRACAS Sheet: {len(df)} satir, {len(df.columns)} sutun")
        except Exception as e:
            print(f"    [Hata] {str(e)[:60]}")

print("\n\n" + "="*120)
print("ARIZA VERİSİ OKUMA MANTIGI".center(120))
print("="*120 + "\n")

logic = """
DASHBOARD'DA ARIZA VERİSİ NASIL OKUNUYOR?

1. get_failures_from_excel() FONKSIYONU:
   - ProjectManager.get_fracas_file() ile FRACAS dosyasını bulur
   - logs/istanbul/ariza_listesi/ klasöründe arar
   - Dosya Adı: Fracas_ISTANBUL.xlsx (türkçe karaktere dikkat!)
   - Sheet: "FRACAS" (header=3, yani 4. satırdan başlıyor)
   - Veri: Son 5 arıza kaydı, arıza sınıflandırması

2. get_today_completed_failures_count() FONKSIYONU:
   - logs/istanbul/ariza_listesi/ klasöründe .xlsx arar
   - Dosya Adı: Ariza_Listesi_ISTANBUL.xlsx
   - Sheet: "Ariza Listesi" (header=3)
   - Veri: Bugünün tamamlanmış arıza sayısı

İSTANBUL İÇİN:
  ✅ FRACAS VERİ KAYNAĞI:
     - Konum: logs/istanbul/ariza_listesi/
     - Dosya: Fracas_ISTANBUL.xlsx
     - Uzantı: .xlsx
     - Sheet: FRACAS
     - Kullanım: Dashboard arıza gösterimi, MTTR hesaplama

  ✅ ARIZA LİSTESİ VERİ KAYNAĞI:
     - Konum: logs/istanbul/ariza_listesi/
     - Dosya: Ariza_Listesi_ISTANBUL.xlsx
     - Uzantı: .xlsx
     - Sheet: Ariza Listesi
     - Kullanım: Bugünün tamamlanan arızaları sayma
"""

print(logic)

print("\n" + "="*120)
print("DOSYA UZANTILARI".center(120))
print("="*120 + "\n")

extensions = """
GERÇEKLEŞTİRME DOSYA UZANTILARI:

┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│ İSTANBUL PROJESİ - ARIZA VERİSİ (Özet Tablosu)                    │
│                                                                     │
│ Dosya Adı                      │ Uzantı  │ Konum             │     │
│ ┌────────────────────────────────────────────────────────────────┤ │
│ │ Fracas_ISTANBUL.xlsx        │ .xlsx   │ logs/istanbul/    │     │
│ │                              │         │ ariza_listesi/    │     │
│ ├────────────────────────────────────────────────────────────────┤ │
│ │ Ariza_Listesi_ISTANBUL.xlsx │ .xlsx   │ logs/istanbul/    │     │
│ │                              │         │ ariza_listesi/    │     │
│ └────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ Tüm dosyalar: Microsoft Excel 2007+ Format (.xlsx)               │
│ Alternativ uzantı: .xls (eski Excel format) - KULLANILMiyor     │
│ CSV format: .csv - KULLANILMiyor                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
"""

print(extensions)

print("\n" + "="*120)
print("VERITABANI - EXCEL SENKRONIZASYONU".center(120))
print("="*120 + "\n")

sync = """
İSTANBUL'UN ARIZA VERİ AKIŞI:

1. Excel Dosyaları (Fracas_ISTANBUL.xlsx + Ariza_Listesi_ISTANBUL.xlsx)
      │
      ├─> get_failures_from_excel() OKUNUR
      │   └─> Fracas_ISTANBUL.xlsx'in "FRACAS" sheet'i
      │       └─> Dashboard'a son 5 arıza gösterilir
      │
      └─> get_today_completed_failures_count() OKUNUR
          └─> Ariza_Listesi_ISTANBUL.xlsx'in "Ariza Listesi" sheet'i
              └─> Bugünün tamamlanan arızaları sayılır

2. Veritabanı Senkronizasyonu:
   - ServiceLog tablosu Excel verilerini kaydeder
   - Equipment tablosu araç bilgilerini kaydeder
   - Failure tablosu arıza kayıtlarını tutar

3. Dashboard Görüntüleme:
   - Son Arızalar (Fracas dosyasından)
   - Arıza Sınıflandırması (A, B, C türleri)
   - Tamamlanmış Arızalar (Ariza Listesi dosyasından)
"""

print(sync)

print("\n" + "="*120)
